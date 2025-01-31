import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool
from azure.identity import DefaultAzureCredential
import json
from pathlib import Path
import matplotlib.pyplot as plt
from collections import Counter
from textblob import TextBlob

# Load environment variables from .env
load_dotenv()

# Ensure the connection string is set
connection_string = os.getenv("PROJECT_CONNECTION_STRING")
if not connection_string:
    raise ValueError("Environment variable 'PROJECT_CONNECTION_STRING' is not set. Please check your .env file.")

# Initialize the Azure AI Project Client
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=connection_string
)

def load_json_file(file_path):
    """Load and return JSON data from a file."""
    try:
        with open(file_path, "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file {file_path}: {e}")
        return None

# Load product and review data
products_data = load_json_file("products.json")
reviews_data = load_json_file("reviews.json")

def analyze_product(product_id):
    """Analyze a specific product by aggregating details and reviews."""
    product_details = next((p for p in products_data if p['ProductId'] == product_id), None)
    product_reviews = [r for r in reviews_data if r['ProductId'] == product_id]

    if not product_details:
        return f"Product with ID {product_id} not found."

    # Aggregate review analysis
    total_reviews = len(product_reviews)
    avg_rating = sum(int(r['Rating']) for r in product_reviews) / total_reviews if total_reviews > 0 else 0

    # Collect review text for further analysis
    review_comments = [r['Comment'] for r in product_reviews]

    # Sentiment analysis
    positive_reviews = []
    negative_reviews = []
    for comment in review_comments:
        polarity = TextBlob(comment).sentiment.polarity
        if polarity > 0:
            positive_reviews.append(comment)
        elif polarity < 0:
            negative_reviews.append(comment)

    # Summarize feedback
    positive_summary = " | ".join(positive_reviews[:3])  # Show up to 3 positive comments
    negative_summary = " | ".join(negative_reviews[:3])  # Show up to 3 negative comments

    # Keyword extraction
    all_words = " ".join(review_comments).lower().split()
    common_keywords = Counter(all_words).most_common(5)

    # Prepare summary
    summary = {
        "Product Name": product_details['Name'],
        "Description": product_details['Description'],
        "Price": product_details['Price'],
        "Average Rating": round(avg_rating, 2),
        "Total Reviews": total_reviews,
        "Sentiment Analysis": {
            "Positive": len(positive_reviews),
            "Neutral": len([TextBlob(comment).sentiment.polarity for comment in review_comments if polarity == 0]),
            "Negative": len(negative_reviews),
            "Positive Summary": positive_summary,
            "Negative Summary": negative_summary,
        },
        "Most Common Keywords": common_keywords
    }
    return summary


def generate_bar_chart(product_id):
    """Generate a bar chart of ratings for a specific product."""
    product_reviews = [r for r in reviews_data if r['ProductId'] == product_id]
    
    if not product_reviews:
        print(f"No reviews found for product ID {product_id}.")
        return

    # Aggregate review counts
    rating_counts = {}
    for review in product_reviews:
        rating = int(review['Rating'])
        rating_counts[rating] = rating_counts.get(rating, 0) + 1

    # Plot the bar chart
    plt.figure(figsize=(8, 6))
    plt.bar(rating_counts.keys(), rating_counts.values(), color='skyblue')
    plt.xlabel('Ratings')
    plt.ylabel('Count')
    plt.title(f'Ratings Distribution for Product ID: {product_id}')
    plt.xticks(range(1, 6))

    # Save the chart
    chart_file = Path(f"rating_distribution_{product_id}.png")
    plt.savefig(chart_file)
    plt.close()
    print(f"Saved chart to: {chart_file}")
    return chart_file

def generate_pie_chart(sentiment_analysis, product_id):
    """Generate a pie chart for sentiment analysis."""
    labels = ['Positive', 'Neutral', 'Negative']
    sizes = [
        sentiment_analysis['Positive'],
        sentiment_analysis['Neutral'],
        sentiment_analysis['Negative']
    ]
    colors = ['#2ecc71', '#95a5a6', '#e74c3c']

    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title(f'Sentiment Analysis for Product ID: {product_id}')

    # Save the chart
    chart_file = Path(f"sentiment_analysis_{product_id}.png")
    plt.savefig(chart_file)
    plt.close()
    print(f"Saved chart to: {chart_file}")
    return chart_file

# Workflow with multiple agents
with project_client:
    # Create CodeInterpreterTool instance
    code_interpreter = CodeInterpreterTool()

    # Create Orchestrator Agent
    orchestrator_agent = project_client.agents.create_agent(
        model="gpt-4o-mini",
        name="orchestrator-agent",
        instructions="Coordinate analysis across product, supplier, and review agents.",
        tools=code_interpreter.definitions,
        tool_resources=code_interpreter.resources,
    )
    print(f"Created orchestrator agent, ID: {orchestrator_agent.id}")

    # Create a thread for interaction
    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    # Product analysis for demo
    product_id = "HT-1000"
    summary = analyze_product(product_id)
    print("Product Summary:", json.dumps(summary, indent=4))

    # Generate charts
    rating_chart_file = generate_bar_chart(product_id)
    sentiment_chart_file = generate_pie_chart(summary['Sentiment Analysis'], product_id)

    # Create and process the run for summary
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=f"Provide an analysis and charts for product ID {product_id}.",
    )
    run = project_client.agents.create_and_process_run(
        thread_id=thread.id, assistant_id=orchestrator_agent.id
    )
    print(f"Run finished with status: {run.status}")

    # Delete agent after use
    project_client.agents.delete_agent(orchestrator_agent.id)
    print("Deleted orchestrator agent.")
