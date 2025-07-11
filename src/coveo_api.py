import requests
import os
import json
import time
from logger import log_error

from dotenv import load_dotenv

# Always load .env from the project root, regardless of where the script is run from
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, '.env'))

API_KEY = os.getenv("COVEO_API_KEY")
BASE_URL = "https://platform-eu.cloud.coveo.com/rest/organizations/{organizationId}/snapshots/self"

def create_snapshot(organization_id, snapshot_name):
    """
    Create a new snapshot with a detailed resourcesToExport body and dynamic developerNotes.

    Args:
        organization_id (str): Coveo organization ID.
        snapshot_name (str): Name for the snapshot.

    Returns:
        str: The ID of the created snapshot.
    """
    url = BASE_URL.format(organizationId=organization_id)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "resourcesToExport": {
            "FIELD": ["*"],
            "EXTENSION": ["*"],
            "QUERY_PIPELINE": ["*"],
            "ML_MODEL": ["*"],
            "SUBSCRIPTION": ["*"],
            "SOURCE": ["*"],
            "SECURITY_PROVIDER": ["*"],
            "CATALOG": ["*"],
            "SEARCH_PAGE": ["*"]
        },
        "developerNotes": f"Snapshot - {snapshot_name}",
        "includeChildrenResources": True
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()["id"]
    except Exception as e:
        log_error(f"Failed to create snapshot: {e}")
        raise

    url = f"{BASE_URL.format(organizationId=organization_id)}/{snapshot_id}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        # Wait for snapshot to be ready (simple polling)
        for _ in range(10):
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "COMPLETED":
                break
            time.sleep(2)
        else:
            raise Exception("Snapshot not ready after waiting.")

        os.makedirs("snapshots", exist_ok=True)
        snapshot_file_path = os.path.join("snapshots", f"{snapshot_name}.json")
        with open(snapshot_file_path, 'w') as snapshot_file:
            json.dump(data, snapshot_file, indent=2)
        return snapshot_file_path
    except Exception as e:
        log_error(f"Failed to export snapshot: {e}")
        raise

def export_snapshot_content(organization_id, snapshot_id, output_path):
    """
    Download the content of a snapshot and save it to output_path.

    Args:
        organization_id (str): Coveo organization ID.
        snapshot_id (str): ID of the snapshot.
        output_path (str): Path where the snapshot content will be saved.

    Returns:
        str: The path to the saved snapshot content file.
    """
    url = f"https://platform-eu.cloud.coveo.com/rest/organizations/{organization_id}/snapshots/{snapshot_id}/content"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path
    except Exception as e:
        log_error(f"Failed to export snapshot content: {e}")
        raise