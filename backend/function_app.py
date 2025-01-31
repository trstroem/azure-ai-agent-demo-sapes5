import os
from dotenv import load_dotenv
import json
import matplotlib.pyplot as plt
from collections import Counter
from textblob import TextBlob
import azure.functions as func
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool
from azure.identity import DefaultAzureCredential

# Initialize Function App (Important for Azure Functions)
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Load environment variables
load_dotenv()
connection_string = os.getenv("PROJECT_CONNECTION_STRING")
if not connection_string:
    raise ValueError("Environment variable 'PROJECT_CONNECTION_STRING' is not set. Please check your .env file.")

# Helper function to load JSON data
def load_json_file(file_path):
    try:
        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, file_path)
        with open(full_path, "r") as json_file:
            return json.load(json_file)
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None

# Load product and review data
products_data = load_json_file("products.json")
reviews_data = load_json_file("reviews.json")

if products_data is None or reviews_data is None:
    raise RuntimeError("Failed to load product or review data. Please check the data files.")

# Analyze a specific product
def analyze_product(product_id):
    product_details = next((p for p in products_data if p['ProductId'] == product_id), None)
    product_reviews = [r for r in reviews_data if r['ProductId'] == product_id]

    if not product_details:
        return {"error": f"Product with ID {product_id} not found."}

    total_reviews = len(product_reviews)
    avg_rating = sum(int(r['Rating']) for r in product_reviews) / total_reviews if total_reviews > 0 else 0
    review_comments = [r['Comment'] for r in product_reviews]

    positive_reviews = [comment for comment in review_comments if TextBlob(comment).sentiment.polarity > 0]
    negative_reviews = [comment for comment in review_comments if TextBlob(comment).sentiment.polarity < 0]

    positive_summary = " | ".join(positive_reviews[:3])
    negative_summary = " | ".join(negative_reviews[:3])

    all_words = " ".join(review_comments).lower().split()
    common_keywords = Counter(all_words).most_common(5)

    return {
        "product_name": product_details['Name'],
        "description": product_details['Description'],
        "price": product_details['Price'],
        "average_rating": round(avg_rating, 2),
        "total_reviews": total_reviews,
        "sentiment_analysis": {
            "positive": len(positive_reviews),
            "negative": len(negative_reviews),
            "positive_summary": positive_summary,
            "negative_summary": negative_summary
        },
        "common_keywords": common_keywords
    }

# Generate bar chart for ratings
def generate_bar_chart(product_id, product_reviews):
    try:
        rating_counts = Counter(int(r["Rating"]) for r in product_reviews)
        output_dir = Path("charts")
        output_dir.mkdir(exist_ok=True)
        file_path = output_dir / f"rating_distribution_{product_id}.png"

        plt.figure(figsize=(8, 6))
        plt.bar(rating_counts.keys(), rating_counts.values(), color="skyblue")
        plt.title(f"Ratings Distribution for Product ID: {product_id}")
        plt.xlabel("Ratings")
        plt.ylabel("Count")
        plt.savefig(file_path)
        plt.close()

        return str(file_path)
    except Exception as e:
        print(f"Error generating bar chart: {e}")
        return None

# Generate pie chart for sentiment analysis
def generate_pie_chart(sentiment_analysis, product_id):
    try:
        labels = ["Positive", "Negative"]
        sizes = [sentiment_analysis["positive"], sentiment_analysis["negative"]]
        colors = ["#2ecc71", "#e74c3c"]
        output_dir = Path("charts")
        output_dir.mkdir(exist_ok=True)
        file_path = output_dir / f"sentiment_analysis_{product_id}.png"

        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=140)
        plt.title(f"Sentiment Analysis for Product ID: {product_id}")
        plt.savefig(file_path)
        plt.close()

        return str(file_path)
    except Exception as e:
        print(f"Error generating pie chart: {e}")
        return None

# Main function exposed as an HTTP trigger
@app.function_name(name="AnalyzeProduct")
@app.route(route="analyze/{product_id}", methods=["GET"])
def main(req: func.HttpRequest) -> func.HttpResponse:
    product_id = req.route_params.get("product_id")
    print(f"Received product_id: {product_id}")

    if not product_id:
        return func.HttpResponse("Missing product_id parameter.", status_code=400)

    try:
        analysis = analyze_product(product_id)
        if "error" in analysis:
            return func.HttpResponse(analysis["error"], status_code=404)

        product_reviews = [r for r in reviews_data if r['ProductId'] == product_id]
        bar_chart_path = generate_bar_chart(product_id, product_reviews)
        pie_chart_path = generate_pie_chart(analysis["sentiment_analysis"], product_id)

        response = {
            "status": "success",
            "product_summary": analysis,
            "bar_chart": bar_chart_path,
            "pie_chart": pie_chart_path,
        }

        with AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(), conn_str=connection_string
        ) as client:
            code_tool = CodeInterpreterTool()
            orchestrator_agent = client.agents.create_agent(
                model="gpt-4o-mini",
                name="orchestrator-agent",
                instructions="Coordinate tasks for product and review analysis.",
                tools=code_tool.definitions,
                tool_resources=code_tool.resources,
            )
            print(f"Created orchestrator agent: {orchestrator_agent.id}")

            thread = client.agents.create_thread()
            print(f"Created thread: {thread.id}")

            message = client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=f"Analyze product {product_id} and generate visualizations.",
            )
            print(f"Created message in thread: {message.id}")

            run = client.agents.create_and_process_run(
                thread_id=thread.id, assistant_id=orchestrator_agent.id
            )
            print(f"Run status: {run.status}")

            response["outputs"] = getattr(run, "outputs", "No outputs available")

            client.agents.delete_agent(orchestrator_agent.id)
            print(f"Deleted orchestrator agent: {orchestrator_agent.id}")

        return func.HttpResponse(
            json.dumps(response, indent=2),
            mimetype="application/json",
            status_code=200,
        )
    except Exception as e:
        print(f"Error during Azure AI Agent workflow: {e}")
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "message": "Failed to process the request.",
                "details": str(e)
            }),
            mimetype="application/json",
            status_code=500,
        )
