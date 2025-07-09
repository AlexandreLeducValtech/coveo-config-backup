import requests
import os
import json
import time
from logger import log_error

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env if present

API_KEY = os.getenv("COVEO_API_KEY")
BASE_URL = "https://platform-eu.cloud.coveo.com/rest/organizations/{organizationId}/snapshots"

def create_snapshot(organization_id, snapshot_name, resources_to_export=None, description=None):
    """
    Create a new snapshot with resources to export and description.

    Args:
        organization_id (str): Coveo organization ID.
        snapshot_name (str): Name for the snapshot.
        resources_to_export (list, optional): List of resources to export. Default is ["ALL"].
        description (str, optional): Description for the snapshot.

    Returns:
        str: The ID of the created snapshot.
    """
    url = BASE_URL.format(organizationId=organization_id)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    if resources_to_export is None:
        resources_to_export = ["ALL"]
    if description is None:
        description = f"Snapshot of the configuration - {time.strftime('%d/%m/%Y')}"
    body = {
        "name": snapshot_name,
        "resourcesToExport": resources_to_export,
        "description": description
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()["id"]
    except Exception as e:
        log_error(f"Failed to create snapshot: {e}")
        raise

def export_snapshot(organization_id, snapshot_id, snapshot_name):
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