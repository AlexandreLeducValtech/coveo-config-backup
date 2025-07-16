import os
import shutil
import time
import tempfile
import re
from datetime import datetime
from coveo_api import create_snapshot, export_snapshot_content, delete_snapshot
from git_utils import commit_snapshot
from compare import compare_jsons_in_zips
from logger import log_info, log_error
from dotenv import load_dotenv

load_dotenv()

# Configuration
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SNAPSHOT_DIR = os.path.join(PROJECT_ROOT, 'snapshots')
REPO_PATH = PROJECT_ROOT  # Root of the repo


def get_latest_snapshot_zip(directory=SNAPSHOT_DIR, pattern=r"snapshot_(\d{8}_\d{6})\.zip$"):
    """Return the path to the most recent snapshot zip file in the given directory, or None if none exist."""
    regex = re.compile(pattern)
    candidates = [(match.group(1), fname) for fname in os.listdir(directory) if (match := regex.match(fname))]
    if not candidates:
        return None
    latest_fname = sorted(candidates, key=lambda x: x[0], reverse=True)[0][1]
    return os.path.join(directory, latest_fname)

def ensure_snapshot_dir_exists():
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)

def wait_for_snapshot_ready(wait_seconds=60):
    log_info(f"Waiting {wait_seconds} seconds for snapshot to be ready...")
    time.sleep(wait_seconds)

def export_snapshot_to_temp_zip(organization_id, snapshot_id):
    """Export snapshot content to a temporary zip file and return its path."""
    ensure_snapshot_dir_exists()
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmpfile:
        temp_zip_path = tmpfile.name
    export_snapshot_content(organization_id, snapshot_id, temp_zip_path)
    log_info(f"Exported new snapshot to temporary file {temp_zip_path}")
    return temp_zip_path

def handle_redundant_snapshot(temp_zip_path, organization_id, snapshot_id):
    os.remove(temp_zip_path)
    log_info("New snapshot is identical to the latest snapshot (JSON content). Deleted redundant snapshot.")
    try:
        delete_snapshot(organization_id, snapshot_id)
        log_info(f"Deleted snapshot {snapshot_id} from Coveo.")
    except Exception as e:
        log_error(f"Failed to delete snapshot {snapshot_id} from Coveo: {e}")

def handle_new_snapshot(temp_zip_path, snapshot_name, organization_id, snapshot_id):
    final_zip_path = os.path.join(SNAPSHOT_DIR, f"{snapshot_name}.zip")
    shutil.move(temp_zip_path, final_zip_path)
    commit_snapshot(final_zip_path, REPO_PATH)
    log_info(f"Committed new snapshot: {final_zip_path}")
    try:
        delete_snapshot(organization_id, snapshot_id)
        log_info(f"Deleted snapshot {snapshot_id} from Coveo.")
    except Exception as e:
        log_error(f"Failed to delete snapshot {snapshot_id} from Coveo: {e}")

def backup_coveo_configuration():
    organization_id = os.getenv("COVEO_ORGANIZATION_ID")
    if not organization_id:
        log_error("COVEO_ORGANIZATION_ID is not set in environment or .env file.")
        return

    snapshot_name = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        # Step 1: Create the snapshot
        snapshot_id = create_snapshot(organization_id, snapshot_name)
        log_info(f"Created snapshot with ID {snapshot_id}")

        # Step 2: Wait for snapshot to be ready
        wait_for_snapshot_ready()

        # Step 3: Export the snapshot content as ZIP to a temp file
        temp_zip_path = export_snapshot_to_temp_zip(organization_id, snapshot_id)

        # Step 4: Compare with the latest snapshot
        latest_snapshot_path = get_latest_snapshot_zip()
        if latest_snapshot_path and compare_jsons_in_zips(temp_zip_path, latest_snapshot_path):
            handle_redundant_snapshot(temp_zip_path, organization_id, snapshot_id)
            return

        # Step 5: Commit the new snapshot to Git and delete from Coveo
        handle_new_snapshot(temp_zip_path, snapshot_name, organization_id, snapshot_id)

    except Exception as e:
        log_error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    backup_coveo_configuration()

