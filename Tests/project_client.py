import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool
from azure.identity import DefaultAzureCredential
from pathlib import Path

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

with project_client:
    # Create an instance of the CodeInterpreterTool
    code_interpreter = CodeInterpreterTool()

    # Create an agent
    agent = project_client.agents.create_agent(
        model="gpt-4o-mini",
        name="my-agent",
        instructions="You are a helpful agent.",
        tools=code_interpreter.definitions,
        tool_resources=code_interpreter.resources,
    )
    print(f"Created agent, agent ID: {agent.id}")

    # Create a thread
    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    # Create a user message
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="Could you please create a bar chart for the operating profit using the following data and provide the file to me? Company A: $1.2 million, Company B: $2.5 million, Company C: $3.0 million, Company D: $1.8 million",
    )
    print(f"Created message, message ID: {message.id}")

    # Run the agent
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")
    else:
        # Get messages from the thread
        messages = project_client.agents.list_messages(thread_id=thread.id)
        print(f"Messages: {messages}")

        # Get the last message from the assistant role
        last_msg = messages.get_last_text_message_by_role("assistant")  # Corrected method
        if last_msg:
            print(f"Last Message: {last_msg.text.value}")

        # Save the generated image file for the bar chart
        for image_content in messages.image_contents:
            file_id = image_content.image_file.file_id
            file_name = f"{file_id}_image_file.png"
            project_client.agents.save_file(file_id=file_id, file_name=file_name)
            print(f"Saved image file to: {Path.cwd() / file_name}")

        # Save file paths from the messages
        for file_path_annotation in messages.file_path_annotations:
            print("File Paths:")
            print(f"Type: {file_path_annotation.type}")
            print(f"Text: {file_path_annotation.text}")
            print(f"File ID: {file_path_annotation.file_path.file_id}")
            print(f"Start Index: {file_path_annotation.start_index}")
            print(f"End Index: {file_path_annotation.end_index}")
            project_client.agents.save_file(
                file_id=file_path_annotation.file_path.file_id,
                file_name=Path(file_path_annotation.text).name
            )

    # Delete the agent once done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")
