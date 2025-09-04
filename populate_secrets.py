import os
import json
import time
from google.cloud import secretmanager
from google.api_core.exceptions import AlreadyExists
import grpc

# Give the emulator a moment to start
time.sleep(5)

project_id = os.environ.get("GCP_PROJECT", "test-project")
emulator_host = os.environ.get("SECRET_MANAGER_EMULATOR_HOST")

if not emulator_host:
    print("SECRET_MANAGER_EMULATOR_HOST not set. Exiting.")
    exit(1)

print(f"Connecting to Secret Manager emulator at {emulator_host}")
channel = grpc.insecure_channel(emulator_host)
client = secretmanager.SecretManagerServiceClient(channel=channel)

parent = f"projects/{project_id}"

secrets_file = os.path.join("data", "secrets.json")

if not os.path.exists(secrets_file):
    print(f"Secrets file not found at {secrets_file}. No secrets to populate.")
    exit(0)

with open(secrets_file, 'r') as f:
    secrets_to_load = json.load(f)

for secret_id, secret_value in secrets_to_load.items():
    secret_path = f"{parent}/secrets/{secret_id}"
    try:
        print(f"Creating secret: {secret_path}")
        client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}},
            }
        )
    except AlreadyExists:
        print(f"Secret {secret_id} already exists.")
        pass
    except Exception as e:
        print(f"An error occurred while creating secret {secret_id}: {e}")
        continue

    try:
        print(f"Adding secret version for {secret_id}")
        client.add_secret_version(
            request={
                "parent": secret_path,
                "payload": {"data": secret_value.encode("UTF-8")},
            }
        )
    except Exception as e:
        print(f"An error occurred while adding a version to secret {secret_id}: {e}")

print("Finished populating secrets.")
