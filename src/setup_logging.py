import logging
import os
import sys


def setup_logging(config):
    log_level = config.get('logging', 'level', fallback='INFO')
    log_path = config.get('logging', 'path', fallback='logs/geo_photo_app.log')
    log_format = config.get('logging', 'format', fallback='%(asctime)s - %(levelname)s - %(message)s')

    log_directory = os.path.dirname(log_path)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory, exist_ok=True)

    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)

    logging.basicConfig(level=numeric_level, encoding='utf-8', format=log_format, filename=log_path)

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        sys.exit(1)

    sys.excepthook = handle_exception
