
from fastapi import APIRouter, HTTPException, Depends
from google.cloud import secretmanager
import os

# Best Practice: Centralize configuration and client initialization.
router = APIRouter()
PROJECT_ID = os.environ.get("GCP_PROJECT")

def get_secret_manager_client():
    """Initializes and returns a Secret Manager client."""
    try:
        return secretmanager.SecretManagerServiceClient()
    except Exception as e:
        # This will fail gracefully if run locally without authentication.
        # In Cloud Run, the service account provides authentication automatically.
        print(f"Could not authenticate with Google Cloud: {e}")
        return None

@router.post("/api/secrets/{secret_id}", status_code=201)
def create_secret(secret_id: str, secret_value: str, client: secretmanager.SecretManagerServiceClient = Depends(get_secret_manager_client)):
    """Creates a new secret and adds its first version."""
    if not client or not PROJECT_ID:
        raise HTTPException(status_code=500, detail="Secret Manager client is not available.")
    
    parent = f"projects/{PROJECT_ID}"
    
    # Create the secret container.
    try:
        response = client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}},
            }
        )
    except Exception as e:
        # Handle cases where the secret might already exist.
        print(e)
        pass

    # Add the secret value as a new version.
    secret_name = f"projects/{PROJECT_ID}/secrets/{secret_id}"
    try:
        client.add_secret_version(
            request={
                "parent": secret_name,
                "payload": {"data": secret_value.encode("UTF-8")},
            }
        )
        return {"status": "success", "secret_id": secret_id, "version": "1"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add secret version: {e}")

@router.get("/api/secrets", response_model=list[str])
def list_secrets(client: secretmanager.SecretManagerServiceClient = Depends(get_secret_manager_client)):
    """Lists the IDs of all secrets in the project."""
    if not client or not PROJECT_ID:
        raise HTTPException(status_code=500, detail="Secret Manager client is not available.")

    parent = f"projects/{PROJECT_ID}"
    secrets = []
    try:
        for secret in client.list_secrets(request={"parent": parent}):
            secret_id = secret.name.split("/")[-1]
            secrets.append(secret_id)
        return secrets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list secrets: {e}")

