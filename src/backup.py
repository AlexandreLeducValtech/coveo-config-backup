import os
import shutil
import time
import tempfile
import re
from datetime import datetime
from coveo_api import create_snapshot, export_snapshot_content
from git_utils import commit_snapshot
from compare import compare_jsons_in_zips
from logger import log_info, log_error
from dotenv import load_dotenv

load_dotenv()

# Configuration
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SNAPSHOT_DIR = os.path.join(PROJECT_ROOT, 'snapshots')
REPO_PATH = PROJECT_ROOT  # Root of the repo

def get_latest_snapshot_path():
    """Return the path to the most recent snapshot_YYYYMMDD_HHMMSS.zip file in SNAPSHOT_DIR, or None if none exist."""
    pattern = re.compile(r"snapshot_(\d{8}_\d{6})\.zip$")
    snapshots = []
    for fname in os.listdir(SNAPSHOT_DIR):
        match = pattern.match(fname)
        if match:
            snapshots.append((match.group(1), fname))
    if not snapshots:
        return None
    latest_fname = sorted(snapshots, key=lambda x: x[0], reverse=True)[0][1]
    return os.path.join(SNAPSHOT_DIR, latest_fname)

def main():
    organization_id = os.getenv("COVEO_ORGANIZATION_ID")
    if not organization_id:
        log_error("COVEO_ORGANIZATION_ID is not set in environment or .env file.")
        return

    snapshot_name = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        # Step 1: Create the snapshot
        snapshot_id = create_snapshot(organization_id, snapshot_name)
        log_info(f"Created snapshot with ID {snapshot_id}")

        # Wait 1 minute before exporting content
        log_info("Waiting 60 seconds for snapshot to be ready...")
        time.sleep(60)

        # Ensure the snapshots directory exists
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)

        # Step 2: Export the snapshot content as ZIP to a temp file
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmpfile:
            temp_zip_path = tmpfile.name
        export_snapshot_content(organization_id, snapshot_id, temp_zip_path)
        log_info(f"Exported new snapshot to temporary file {temp_zip_path}")

        # Step 3: Compare with the latest snapshot
        latest_snapshot_path = get_latest_snapshot_path()
        if latest_snapshot_path and compare_jsons_in_zips(temp_zip_path, latest_snapshot_path):
            os.remove(temp_zip_path)
            log_info("New snapshot is identical to the latest snapshot (JSON content). Deleted redundant snapshot.")
            return

        # Step 4: Commit the new snapshot to Git and update latest reference
        final_zip_path = os.path.join(SNAPSHOT_DIR, f"{snapshot_name}.zip")
        shutil.move(temp_zip_path, final_zip_path)
        commit_snapshot(final_zip_path, REPO_PATH)
        # Optionally, update a 'latest_snapshot.zip' pointer file if you want
        log_info(f"Committed new snapshot: {final_zip_path}")

    except Exception as e:
        log_error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()