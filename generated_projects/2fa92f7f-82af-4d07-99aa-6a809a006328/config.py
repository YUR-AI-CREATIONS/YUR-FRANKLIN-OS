"""
Configuration settings for the application.
"""

import os
from pathlib import Path

# Application settings
APP_NAME = "Python Code Demo"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Generated Code"

# File paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Environment settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Default file names
DEFAULT_OUTPUT_FILE = "sample_output.txt"
DEFAULT_DATA_FILE = "data.json"
DEFAULT_LOG_FILE = "app.log"

# Application constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_FORMATS = [".txt", ".json", ".csv", ".log"]