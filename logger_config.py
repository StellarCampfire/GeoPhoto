import logging
import os
import sys

def setup_logging():
    log_directory = "logs"
    log_filename = os.path.join(log_directory, 'geo_photo_app.log')

    os.makedirs(log_directory, exist_ok=True)

    logging.basicConfig(level=logging.INFO, encoding='utf-8', format='%(asctime)s - %(levelname)s - %(message)s', filename=log_filename)

    # Функция для перехвата исключений
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        sys.exit(1)

    # Установка глобального обработчика исключений
    sys.excepthook = handle_exception

