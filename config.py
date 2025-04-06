# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file (project root or current directory)
load_dotenv()

# For Replicate you may need to set REPLICATE_API_TOKEN as well,
# but if using replicate's default behavior, it will check your environment.
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise ValueError("Missing REPLICATE_API_TOKEN environment variable.")
