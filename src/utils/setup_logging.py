import logging
import os
import sys


def setup_logging(log_level='INFO'):
    log_path = 'logs/geo_photo_app.log'  # Path to the log file
    log_format = '%(asctime)s - %(levelname)s - %(message)s'  # Logging format

    # Create the log directory if it doesn't exist
    log_directory = os.path.dirname(log_path)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory, exist_ok=True)

    # Set the logging level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)

    # Configure basic logging settings
    handlers = [logging.FileHandler(log_path, encoding='utf-8')]
    logging.basicConfig(level=numeric_level, format=log_format, handlers=handlers)

    # Intercept exceptions for logging uncaught exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        sys.exit(1)

    sys.excepthook = handle_exception
