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

1. **Clone the Repository**: 
   Clone this repository to your local machine using Git.

   ```
   git clone git@github.com:AlexandreLeducValtech/coveo-config-backup.git
   ```

2. **Install Dependencies**: 
   Navigate to the project directory and install the required Python packages listed in `requirements.txt`.

   ```
   cd coveo-config-backup
   pip install -r requirements.txt
   ```

3. **Configure API Access**: 
   Ensure you have access to the Coveo API and configure any necessary authentication details in the `coveo_api.py` file.

## Usage

To run the backup process, execute the `backup.py` script:

```
python src/backup.py
```

This script will:
- Export the current configuration snapshot from the Coveo API.
- Compare it with the most recent snapshot.
- If the snapshots are different, it will commit the new snapshot to the Git repository with a timestamped message.

## Logging

The application logs its operations and errors. Check the logs to troubleshoot any issues that may arise during the backup process.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.