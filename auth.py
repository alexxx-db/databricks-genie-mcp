import os
import logging
from typing import Optional
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv  # Add this import


load_dotenv()
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_workspace_client() -> WorkspaceClient:
    """
    Create a Databricks WorkspaceClient with authentication from environment variables.
    
    This function supports multiple authentication methods:
    1. Personal Access Token (PAT) authentication
    2. OAuth authentication (via service principal)
    
    Required environment variables:
    - DATABRICKS_HOST: The URL of your Databricks workspace
    
    And one of:
    - DATABRICKS_TOKEN: For PAT authentication
    - DATABRICKS_CLIENT_ID and DATABRICKS_CLIENT_SECRET: For OAuth with service principal
    
    Returns:
        WorkspaceClient: An authenticated Databricks workspace client
    
    Raises:
        ValueError: If required environment variables are missing
        Exception: If authentication fails
    """
    # Check for required environment variables
    host = os.environ.get("DATABRICKS_HOST")
    if not host:
        raise ValueError("DATABRICKS_HOST environment variable is required")
    
    # Check authentication method
    token = os.environ.get("DATABRICKS_TOKEN")
    client_id = os.environ.get("DATABRICKS_CLIENT_ID")
    client_secret = os.environ.get("DATABRICKS_CLIENT_SECRET")
    
    # Initialize workspace client with appropriate authentication
    try:
        if token:
            # PAT authentication
            logger.info("Using personal access token authentication")
            client = WorkspaceClient(host=host, token=token)
        elif client_id and client_secret:
            # OAuth with service principal
            logger.info("Using OAuth service principal authentication")
            client = WorkspaceClient(
                host=host,
                client_id=client_id,
                client_secret=client_secret
            )
        else:
            # Try default authentication (e.g., from ~/.databrickscfg)
            logger.info("Using default authentication from config")
            client = WorkspaceClient()
        
        # Test the connection
        me = client.current_user.me()
        logger.info(f"Successfully authenticated as user: {me.user_name}")
        
        return client
        
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise Exception(f"Failed to authenticate with Databricks: {str(e)}")

def test_genie_access(client: WorkspaceClient) -> bool:
    """
    Test access to the Genie API.
    
    Args:
        client: Authenticated Databricks WorkspaceClient
    
    Returns:
        bool: True if Genie API is accessible, False otherwise
    """
    try:
        # Try to access the genie attribute
        if hasattr(client, 'genie'):
            logger.info("Genie API is available")
            return True
        else:
            logger.warning("Genie API is not available in this client")
            return False
    except Exception as e:
        logger.error(f"Error accessing Genie API: {str(e)}")
        return False 