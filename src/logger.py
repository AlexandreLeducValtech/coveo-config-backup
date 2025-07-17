import logging
import os

def setup_logger(log_file='backup.log'):
    """Sets up the logger for the application."""
    logger = logging.getLogger('CoveoConfigBackup')
    logger.setLevel(logging.DEBUG)

    # Avoid adding handlers multiple times
    if not logger.handlers:
        # Create a file handler to log to a file
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.FileHandler(os.path.join('logs', log_file))
        file_handler.setLevel(logging.DEBUG)

        # Create a console handler to log to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create a formatter and set it for both handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()

def log_info(message):
    logger.info(message)
    _trim_log_file()

def log_error(message):
    logger.error(message)
    _trim_log_file()

def _trim_log_file(log_path=os.path.join('logs', 'backup.log'), max_lines=500):
    """Trim the log file to the last max_lines lines if it exceeds that number."""
    try:
        if os.path.exists(log_path):
            with open(log_path, 'r+') as f:
                lines = f.readlines()
                if len(lines) > max_lines:
                    f.seek(0)
                    f.writelines(lines[-max_lines:])
                    f.truncate()
    except Exception as e:
        # Avoid logging here to prevent recursion
        pass
