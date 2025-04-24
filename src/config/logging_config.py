import logging
import logging.handlers
import os
import sys

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FILE_PATH = "./logs/app.log"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

def setup_logging():
    """Configures application-wide logging.

    Sets up logging to both console (stdout) and a rotating file.
    Log level and file path are configurable via environment variables
    LOG_LEVEL and LOG_FILE_PATH respectively.
    """
    log_level_str = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
    log_file_path = os.getenv("LOG_FILE_PATH", DEFAULT_LOG_FILE_PATH)

    if log_level_str not in VALID_LOG_LEVELS:
        print(f"Warning: Invalid LOG_LEVEL '{log_level_str}'. Defaulting to {DEFAULT_LOG_LEVEL}.", file=sys.stderr)
        log_level_str = DEFAULT_LOG_LEVEL

    log_level = getattr(logging, log_level_str)

    # Create log directory if it doesn't exist
    try:
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    except OSError as e:
        print(f"Error creating log directory '{log_dir}': {e}", file=sys.stderr)
        # Continue without file logging if directory creation fails
        log_file_path = None 

    # --- Root Logger Configuration --- 
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level) # Set root logger level

    # Clear existing handlers (important for Streamlit)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    formatter = logging.Formatter(LOG_FORMAT)

    # --- Console Handler --- 
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # --- Rotating File Handler --- 
    if log_file_path:
        try:
            # Rotate logs at 10MB, keep 3 backups
            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path, maxBytes=10*1024*1024, backupCount=3, encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            logging.info(f"File logging configured to: {log_file_path}")
        except Exception as e:
            logging.error(f"Failed to configure file logging to '{log_file_path}': {e}", exc_info=True)
    else:
        logging.warning("File logging disabled as log directory could not be created.")

    logging.info(f"Logging configured. Level: {log_level_str}") 