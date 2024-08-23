import logging
import os
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self, log_dir, log_file_name, log_level=logging.INFO, max_bytes=10485760, backup_count=5):
        self.log_dir = log_dir
        self.log_file_name = log_file_name
        self.log_level = log_level
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        self.logger = logging.getLogger(self.log_file_name)
        self.logger.setLevel(self.log_level)

        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.setup_file_handler()
        self.setup_console_handler()

    def setup_file_handler(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        log_file_path = os.path.join(self.log_dir, f"{self.log_file_name}.log")

        # Check if the log file exists and delete it
        if os.path.isfile(log_file_path):
            try:
                os.remove(log_file_path)
                self.logger.info(f"Deleted existing log file: {log_file_path}")
            except Exception as e:
                self.logger.error(f"Error deleting log file: {e}")

        file_handler = RotatingFileHandler(log_file_path, maxBytes=self.max_bytes, backupCount=self.backup_count)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    def setup_console_handler(self):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger

    def log(self, log_level, message):
        if log_level == logging.DEBUG:
            self.logger.debug(message)
        elif log_level == logging.INFO:
            self.logger.info(message)
        elif log_level == logging.WARNING:
            self.logger.warning(message)
        elif log_level == logging.ERROR:
            self.logger.error(message)
        elif log_level == logging.CRITICAL:
            self.logger.critical(message)
        else:
            raise ValueError("Invalid log level provided")
