def commit_snapshot(snapshot_path, repo_path):
    import os
    import git
    from datetime import datetime

    try:
        # Initialize the Git repository
        repo = git.Repo(repo_path)

        # Add the new snapshot to the staging area
        repo.index.add([snapshot_path])

        # Create a commit message with a timestamp
        commit_message = f"Backup snapshot: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {os.path.basename(snapshot_path)}"

        # Commit the changes
        repo.index.commit(commit_message)

        print(f"Committed new snapshot: {commit_message}")

    except Exception as e:
        print(f"Error committing snapshot: {e}")


def check_if_identical(snapshot1_path, snapshot2_path):
    import filecmp

    # Compare the two snapshot files
    return filecmp.cmp(snapshot1_path, snapshot2_path, shallow=False)