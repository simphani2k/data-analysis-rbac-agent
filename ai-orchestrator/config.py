import os
from pathlib import Path
from dotenv import load_dotenv

# Detect environment: dev or prod
ENV = os.getenv("APP_ENV", "dev")  # default to dev

# Load the correct .env file
base_dir = Path(__file__).resolve().parent
env_file = base_dir / (".env.prod" if ENV == "prod" else ".env.dev")
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    print(f"Warning: {env_file} not found, relying on system environment variables")

# Now load your variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL")
GROQ_MODEL = os.getenv("GROQ_MODEL")

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT")

# Sanity checks
if not GROQ_API_KEY or not GROQ_API_URL:
    raise RuntimeError("GROQ_API_KEY or GROQ_API_URL not set!")