import sys
import argparse
import logging

from src.utils.setup_logging import setup_logging
from src.utils.config_manager import ConfigManager
from src.core.app import App

from PyQt5.QtWidgets import QApplication


def parse_args():
    parser = argparse.ArgumentParser(description="Run the PyQt5 application.")
    parser.add_argument('--resolution', type=str, help='Window resolution in WIDTHxHEIGHT format, e.g., 1280x720')
    parser.add_argument('--log-level', type=str, default='INFO',
                        help='Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--emulate', action='store_true', help='Use camera emulator instead of real cameras')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    setup_logging(args.log_level)

    logging.debug("Starting application setup.")
    config_manager = ConfigManager()
    logging.debug("ConfigManager initialized.")

    logging.info(f"Application will run with resolution: {args.resolution if args.resolution else 'fullscreen'}")

    qt_app = QApplication(sys.argv)
    logging.debug("QApplication instance created.")

    app = App(sys.argv, config_manager, resolution=args.resolution, emulate=args.emulate)
    logging.info("Application instance created and configured.")

    exit_code = qt_app.exec_()
    logging.info("Application execution finished.")
    sys.exit(exit_code)
