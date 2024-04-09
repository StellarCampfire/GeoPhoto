import logging
import os
import sys


def setup_logging(log_level='INFO'):
    log_path = 'logs/geo_photo_app.log'  # Путь к файлу лога
    log_format = '%(asctime)s - %(levelname)s - %(message)s'  # Формат логирования

    # Создаем директорию для логов, если она еще не существует
    log_directory = os.path.dirname(log_path)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory, exist_ok=True)

    # Устанавливаем уровень логирования
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)

    # Настраиваем базовую конфигурацию логирования
    handlers = [logging.FileHandler(log_path, encoding='utf-8')]
    logging.basicConfig(level=numeric_level, format=log_format, handlers=handlers)

    # Перехват исключений для логирования неотловленных исключений
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        sys.exit(1)

    sys.excepthook = handle_exception
