import logging
import os

def setup_logging(log_file='logs/ids.log'):
    """Sets up logging configuration."""
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))
    
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )

def log_event(message):
    """Logs an event message."""
    logging.info(message)

def log_error(message):
    """Logs an error message."""
    logging.error(message)