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

def log_error(message):
    logger.error(message)
