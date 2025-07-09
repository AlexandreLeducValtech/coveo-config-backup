import os
import shutil
from datetime import datetime
from coveo_api import create_snapshot, export_snapshot
from git_utils import commit_snapshot
from compare import are_snapshots_identical
from logger import log_info, log_error

from dotenv import load_dotenv
load_dotenv()

# Configuration
SNAPSHOT_DIR = 'snapshots'
LATEST_SNAPSHOT = os.path.join(SNAPSHOT_DIR, 'latest_snapshot.json')
REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # Root of the repo

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

        # Step 2: Export the snapshot
        new_snapshot_path = export_snapshot(organization_id, snapshot_id, snapshot_name)
        log_info(f"Exported new snapshot to {new_snapshot_path}")

        # Step 3: Compare with the latest snapshot
        if os.path.exists(LATEST_SNAPSHOT):
            if are_snapshots_identical(new_snapshot_path, LATEST_SNAPSHOT):
                os.remove(new_snapshot_path)
                log_info("New snapshot is identical to the latest snapshot. Deleted redundant snapshot.")
            else:
                # Step 4: Commit the new snapshot to Git
                commit_snapshot(new_snapshot_path, REPO_PATH)
                shutil.copy(new_snapshot_path, LATEST_SNAPSHOT)
                log_info(f"Committed new snapshot and updated latest snapshot reference.")
        else:
            # If no latest snapshot exists, just commit the new one
            commit_snapshot(new_snapshot_path, REPO_PATH)
            shutil.copy(new_snapshot_path, LATEST_SNAPSHOT)
            log_info("No previous snapshot found. Committed the initial snapshot.")

    except Exception as e:
        log_error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()