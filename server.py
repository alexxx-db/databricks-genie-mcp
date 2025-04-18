from typing import Any, Dict, List, Optional
import os
import json
import time
from mcp.server.fastmcp import FastMCP
from databricks.sdk import WorkspaceClient

# Import authentication utilities
from auth import get_workspace_client

# Initialize FastMCP server
mcp = FastMCP("genie")

# Initialize Databricks client (will be set in main)
databricks_client = None

@mcp.tool()
async def start_conversation(space_id: str, content: str) -> Dict[str, Any]:
    """Start a new conversation in a Genie space.
    
    Args:
        space_id: The ID associated with the Genie space where you want to start a conversation
        content: The text of the message that starts the conversation
    """
    if not databricks_client:
        return {"error": "Databricks client not initialized. Check authentication."}
    
    try:
        # Call the Genie API to start a conversation
        genie_api = databricks_client.genie
        message = genie_api.start_conversation_and_wait(space_id, content)
        
        # Format the response for better readability, modeling it after the REST API response
        response = {
            "conversation_id": message.conversation_id,
            "message_id": message.message_id,
            "content": message.content,
            "status": message.status.value if message.status else None,
            # Include any attachments if present
            "attachments": getattr(message, 'attachments', None)
        }
        
        return response
    except Exception as e:
        return {"error": f"Error starting conversation: {str(e)}"}

@mcp.tool()
async def create_message(space_id: str, conversation_id: str, content: str) -> Dict[str, Any]:
    """Create a new message in an existing conversation.
    
    Args:
        space_id: The ID associated with the Genie space where the conversation is located
        conversation_id: The ID of the conversation
        content: The text of the new message
    """
    if not databricks_client:
        return {"error": "Databricks client not initialized. Check authentication."}
    
    try:
        # Call the Genie API to create a message
        genie_api = databricks_client.genie
        message = genie_api.create_message_and_wait(space_id, conversation_id, content)
        
        # Format the response for better readability, modeling it after the REST API response
        return {
            "message_id": message.message_id,
            "content": message.content,
            "status": message.status.value if message.status else None,
            # Include any attachments if present
            "attachments": getattr(message, 'attachments', None),
            "conversation_id": message.conversation_id
        }
    except Exception as e:
        return {"error": f"Error creating message: {str(e)}"}

@mcp.tool()
async def get_message(space_id: str, conversation_id: str, message_id: str) -> Dict[str, Any]:
    """Get a message from a conversation.
    
    Args:
        space_id: The ID associated with the Genie space where the conversation is located
        conversation_id: The ID of the conversation
        message_id: The ID of the message to retrieve
    """
    if not databricks_client:
        return {"error": "Databricks client not initialized. Check authentication."}
    
    try:
        # Call the Genie API to get a message
        genie_api = databricks_client.genie
        message = genie_api.get_message(space_id, conversation_id, message_id)
        
        # Format the response for better readability, modeling it after the REST API response
        response = {
            "message_id": message.message_id,
            "content": message.content,
            "status": message.status.value if message.status else None,
            "conversation_id": message.conversation_id,
            "space_id": space_id,
            # Include any attachments if present
            "attachments": getattr(message, 'attachments', None),
            "error": getattr(message, 'error', None)
        }
        
        return response
    except Exception as e:
        return {"error": f"Error retrieving message: {str(e)}"}

@mcp.tool()
async def get_message_attachment_query_result(
    space_id: str, 
    conversation_id: str, 
    message_id: str, 
    attachment_id: str
) -> Dict[str, Any]:
    """Get the SQL query result from a message attachment.
    
    Args:
        space_id: The ID of the Genie space
        conversation_id: The ID of the conversation
        message_id: The ID of the message
        attachment_id: The ID of the query attachment
    """
    if not databricks_client:
        return {"error": "Databricks client not initialized. Check authentication."}
    
    try:
        # Call the Genie API to get query results
        genie_api = databricks_client.genie
        result = genie_api.get_message_attachment_query_result(
            space_id, conversation_id, message_id, attachment_id
        )
        
        # Return the statement response details
        if result.statement_response:
            # Convert StatementResponse to dict for serialization
            # Note: This might include complex nested objects. 
            # Adjust if a flatter structure is preferred.
            return result.statement_response.as_dict()
        else:
            return {"error": "No statement response found."}
    except Exception as e:
        return {"error": f"Error retrieving query result: {str(e)}"}

@mcp.tool()
async def execute_message_attachment_query(
    space_id: str, 
    conversation_id: str, 
    message_id: str, 
    attachment_id: str
) -> Dict[str, Any]:
    """Execute the SQL query for a message attachment.
    
    Args:
        space_id: The ID of the Genie space
        conversation_id: The ID of the conversation
        message_id: The ID of the message
        attachment_id: The ID of the query attachment
    """
    if not databricks_client:
        return {"error": "Databricks client not initialized. Check authentication."}
    
    try:
        # Call the Genie API to execute the query
        genie_api = databricks_client.genie
        result = genie_api.execute_message_attachment_query(
            space_id, conversation_id, message_id, attachment_id
        )
        
        # Return the statement response details
        if result.statement_response:
            # Convert StatementResponse to dict for serialization
            # Note: This might include complex nested objects. 
            # Adjust if a flatter structure is preferred.
            return result.statement_response.as_dict()
        else:
            return {"error": "No statement response found."}
    except Exception as e:
        return {"error": f"Error executing query: {str(e)}"}

@mcp.tool()
async def get_space(space_id: str) -> Dict[str, Any]:
    """Get details of a Genie Space.
    
    Args:
        space_id: The ID of the Genie space to retrieve details for
    """
    if not databricks_client:
        return {"error": "Databricks client not initialized. Check authentication."}
    
    try:
        # Call the Genie API to get space details
        genie_api = databricks_client.genie
        space = genie_api.get_space(space_id)
        
        # Format the response for better readability
        # The space object is returned directly from the API
        return {
            "space_id": space_id,  # Use the provided space_id since it's not in the object
            "title": space.title,
            "description": getattr(space, 'description', None)
        }
    except Exception as e:
        return {"error": f"Error retrieving space: {str(e)}"}

@mcp.tool()
async def generate_download_full_query_result(
    space_id: str, 
    conversation_id: str, 
    message_id: str, 
    attachment_id: str
) -> Dict[str, Any]:
    """Generate full query result download.
    
    Args:
        space_id: The ID of the Genie space
        conversation_id: The ID of the conversation
        message_id: The ID of the message
        attachment_id: The ID of the query attachment
    """
    if not databricks_client:
        return {"error": "Databricks client not initialized. Check authentication."}
    
    try:
        # Call the Genie API to generate download for full query result
        genie_api = databricks_client.genie
        result = genie_api.generate_download_full_query_result(
            space_id, conversation_id, message_id, attachment_id
        )
        
        # Format the response for better readability
        return {
            "transient_statement_id": result.transient_statement_id,
            "status": result.status.value if result.status else None
        }
    except Exception as e:
        return {"error": f"Error generating download for query result: {str(e)}"}

@mcp.tool()
async def poll_message_until_complete(
    space_id: str,
    conversation_id: str,
    message_id: str,
    timeout_seconds: int = 600,
    poll_interval_seconds: int = 5
) -> Dict[str, Any]:
    """Poll a message until its status is COMPLETED or until timeout.
    
    Args:
        space_id: The ID of the Genie space
        conversation_id: The ID of the conversation
        message_id: The ID of the message
        timeout_seconds: Maximum time to poll (default: 10 minutes)
        poll_interval_seconds: Time between polls (default: 5 seconds)
    """
    if not databricks_client:
        return {"error": "Databricks client not initialized. Check authentication."}
    
    try:
        # Initialize variables for polling
        start_time = time.time()
        elapsed_time = 0
        poll_count = 0
        
        # Poll until status is COMPLETED or timeout
        while elapsed_time < timeout_seconds:
            # Get message status
            genie_api = databricks_client.genie
            message = genie_api.get_message(space_id, conversation_id, message_id)
            status = message.status.value if message.status else "UNKNOWN"
            poll_count += 1
            
            # Format message for response
            formatted_message = {
                "message_id": message.message_id,
                "content": message.content,
                "status": status,
                "conversation_id": message.conversation_id,
                "space_id": space_id,
                "attachments": getattr(message, 'attachments', None),
                "error": getattr(message, 'error', None),
                "poll_count": poll_count,
                "elapsed_time": elapsed_time
            }
            
            # Check if status is terminal
            if status == "COMPLETED":
                return formatted_message
            elif status in ["FAILED", "QUERY_RESULT_EXPIRED", "CANCELLED"]:
                return formatted_message
            
            # Sleep for poll_interval_seconds
            time.sleep(poll_interval_seconds)
            
            # Implement exponential backoff after 2 minutes
            if elapsed_time > 120 and poll_interval_seconds < 30:
                poll_interval_seconds = min(poll_interval_seconds * 1.5, 30)
            
            # Update elapsed time
            elapsed_time = time.time() - start_time
        
        # If we reached timeout
        return {
            "error": f"Timeout after {timeout_seconds} seconds",
            "message_id": message_id,
            "conversation_id": conversation_id,
            "space_id": space_id,
            "status": status,
            "poll_count": poll_count,
            "elapsed_time": elapsed_time
        }
            
    except Exception as e:
        return {"error": f"Error polling message: {str(e)}"}

def initialize_client():
    """Initialize the Databricks client with authentication."""
    try:
        client = get_workspace_client()
        print(f"Successfully connected to Databricks workspace: {os.environ.get('DATABRICKS_HOST', 'Unknown')}")
        return client
    except Exception as e:
        print(f"Warning: Failed to initialize Databricks client: {e}")
        print("The server will start, but Genie API tools will not function until authentication is fixed.")
        return None

if __name__ == "__main__":
    print("Initializing Databricks Genie MCP Server...")
    
    # Initialize the Databricks client with authentication
    databricks_client = initialize_client()

    # Initialize and run the server
    print("Starting MCP server with Genie API tools...")
    mcp.run(transport='stdio') 