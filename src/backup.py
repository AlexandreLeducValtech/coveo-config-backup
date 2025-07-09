import os
import shutil
import subprocess
import re
from datetime import datetime
from git_utils import commit_snapshot
from compare import are_snapshots_identical
from logger import log_info, log_error

from dotenv import load_dotenv
load_dotenv()

# Configuration
SNAPSHOT_DIR = 'snapshots'
LATEST_SNAPSHOT = os.path.join(SNAPSHOT_DIR, 'latest_snapshot')
REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # Root of the repo

def create_snapshot_with_cli(organization_id, snapshot_name):
    snapshot_dir = os.path.join(SNAPSHOT_DIR, snapshot_name)
    os.makedirs(snapshot_dir, exist_ok=True)

    # Step 1: Start snapshot creation
    cmd = [
        "coveo", "org:resources:pull",
        "-o", organization_id,
        "-f"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=snapshot_dir)
        log_info(f"CLI output: {result.stdout}")

        # Step 2: Parse snapshotId from output
        match = re.search(r'org:resources:monitor ([\w\-]+)', result.stdout)
        if not match:
            log_error("Could not find snapshotId in CLI output.")
            raise Exception("SnapshotId not found in CLI output.")
        snapshot_id = match.group(1)
        log_info(f"Parsed snapshotId: {snapshot_id}")

        # Step 3: Monitor snapshot creation
        monitor_cmd = [
            "coveo", "org:resources:monitor", snapshot_id
        ]
        log_info("Monitoring snapshot creation...")
        monitor_result = subprocess.run(monitor_cmd, capture_output=True, text=True, check=True)
        log_info(f"Monitor output: {monitor_result.stdout}")

        # Step 4: Pull the completed snapshot
        pull_cmd = [
            "coveo", "org:resources:pull",
            "-o", organization_id,
            "-f",
            "-s", snapshot_id
        ]
        pull_result = subprocess.run(pull_cmd, capture_output=True, text=True, check=True, cwd=snapshot_dir)
        log_info(f"Final pull output: {pull_result.stdout}")

        return snapshot_dir
    except subprocess.CalledProcessError as e:
        log_error(f"Failed to create snapshot with CLI: {e.stderr}")
        raise

def main():
    organization_id = os.getenv("COVEO_ORGANIZATION_ID")
    if not organization_id:
        log_error("COVEO_ORGANIZATION_ID is not set in environment or .env file.")
        return

    snapshot_name = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        # Step 1: Create the snapshot using CLI
        new_snapshot_path = create_snapshot_with_cli(organization_id, snapshot_name)
        log_info(f"Exported new snapshot to {new_snapshot_path}")

        # Step 2: Compare with the latest snapshot (as directories)
        if os.path.exists(LATEST_SNAPSHOT):
            if are_snapshots_identical(new_snapshot_path, LATEST_SNAPSHOT):
                shutil.rmtree(new_snapshot_path)
                log_info("New snapshot is identical to the latest snapshot. Deleted redundant snapshot.")
            else:
                # Step 3: Commit the new snapshot to Git
                commit_snapshot(new_snapshot_path, REPO_PATH)
                # Update latest snapshot reference
                if os.path.exists(LATEST_SNAPSHOT):
                    shutil.rmtree(LATEST_SNAPSHOT)
                shutil.copytree(new_snapshot_path, LATEST_SNAPSHOT)
                log_info("Committed new snapshot and updated latest snapshot reference.")
        else:
            # If no latest snapshot exists, just commit the new one
            commit_snapshot(new_snapshot_path, REPO_PATH)
            shutil.copytree(new_snapshot_path, LATEST_SNAPSHOT)
            log_info("No previous snapshot found. Committed the initial snapshot.")

    except Exception as e:
        log_error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()