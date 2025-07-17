# Coveo Configuration Backup

This project automates the backup and versioning of Coveo configuration snapshots using the Coveo API and Git.

## Project Structure

```
coveo-config-backup
├── src
│   ├── backup.py          # Main script to orchestrate the backup process
│   ├── coveo_api.py       # Functions to interact with the Coveo API
│   ├── git_utils.py       # Utility functions for Git operations
│   ├── compare.py         # Logic to compare snapshots
│   └── logger.py          # Logging setup for the application
├── snapshots              # Directory for storing exported configuration snapshots
├── requirements.txt       # Python dependencies required for the project
└── README.md              # Project documentation
```

## Setup Instructions

### 1. Clone the Repository

Clone this repository to your local machine:

```sh
git clone git@github.com:AlexandreLeducValtech/coveo-config-backup.git
```

### 2. Install Dependencies

Navigate to the project directory and install required Python packages:

```sh
cd coveo-config-backup
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root with your Coveo API key:

```
COVEO_API_KEY=your_coveo_api_key_here
```

### 4. (Optional) Python Environment

It is recommended to use a virtual environment:

```sh
python3 -m venv venv
source venv/bin/activate
```

### 5. API Access

Ensure your API key has sufficient permissions to create, export, and delete snapshots in your Coveo organization.

---

## Usage

To run the backup process, execute:

```sh
python src/backup.py
```

This script will:

- Export the current configuration snapshot from the Coveo API.
- Compare it with the most recent snapshot in the `snapshots/` directory.
- If the snapshots are different, commit the new snapshot to the Git repository with a timestamped message.

### Advanced Usage

- **Manual snapshot export:** Use functions in `src/coveo_api.py` for custom exports.
- **Compare snapshots:** Use `src/compare.py` to compare two snapshot ZIPs.
- **Git operations:** Use `src/git_utils.py` for custom commit or comparison logic.

---

## Logging

All operations and errors are logged to `logs/backup.log` and the console. Review logs for troubleshooting and audit purposes.

---

## Contributing

Contributions are welcome! Please:

- Fork the repository and create a feature branch.
- Follow PEP8 and write clear commit messages.
- Submit a pull request with a description of your changes.
- Open an issue for bug reports or feature requests.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Troubleshooting

- **Authentication errors:** Ensure your `.env` file is present and contains a valid API key.
- **Permission errors:** Verify your API key permissions in Coveo.
- **Dependency issues:** Run `pip install -r requirements.txt` to install missing packages.
- **Snapshot not committed:** Check logs for errors and ensure your Git repository is initialized.

## Environment

- **Python:** 3.9+
- **OS:** macOS, Linux, Windows
- **Dependencies:** See `requirements.txt`

## Maintainers

For questions or support, contact [Alexandre Leduc](mailto:alexandre.leduc@valtech.com).
