import os
from google.cloud import secretmanager
from google.api_core.exceptions import NotFound, GoogleAPICallError
from svc.core.logging import setup_logging

logger = setup_logging()

class SecretManager: 
    def __init__(self):
        self.project_id = os.environ.get("GCP_PROJECT")
        if not self.project_id:
            logger.error("GCP_PROJECT environment variable not set.")
            raise ValueError("GCP_PROJECT environment variable not set.")
        self.client = secretmanager.SecretManagerServiceClient()

    def get_secret(self, secret_id: str, version: str = "latest") -> str:
        """
        Retrieves a secret's payload from Google Secret Manager.
        """
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
        try:
            response = self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except NotFound:
            logger.error(f"Secret '{secret_id}' with version '{version}' not found.")
            return None
        except GoogleAPICallError as e:
            logger.error(f"Error accessing secret '{secret_id}': {e}")
            return None

    def update_secret(self, secret_id: str, payload: str) -> str:
        """
        Creates a new version of a secret with the given payload.
        """
        parent = f"projects/{self.project_id}/secrets/{secret_id}"
        payload_bytes = payload.encode("UTF-8")
        try:
            response = self.client.add_secret_version(
                request={
                    "parent": parent,
                    "payload": {"data": payload_bytes},
                }
            )
            version = response.name.split("/")[-1]
            logger.info(f"Added new version '{version}' to secret '{secret_id}'.")
            return version
        except NotFound:
            logger.error(f"Secret '{secret_id}' not found. Cannot add a new version.")
            return None
        except GoogleAPICallError as e:
            logger.error(f"Error updating secret '{secret_id}': {e}")
            return None

secrets_client = SecretManager()
