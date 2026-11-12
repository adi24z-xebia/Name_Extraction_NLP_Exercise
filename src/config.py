
from pathlib import Path

# Absolute project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# File locations
INPUT_FILE = BASE_DIR / "data" / "input" / "emails.csv"
OUTPUT_FILE = BASE_DIR / "data" / "output" / "submission.csv"

# Input schema
INPUT_COLUMNS = ["ID", "data"]

# Submission schema
OUTPUT_COLUMNS = [
    "ID",
    "all_names",
    "sender",
    "recipients",
]

# Processing configuration
BATCH_SIZE = 100

ENGLISH_MODEL = "en_core_web_sm"
