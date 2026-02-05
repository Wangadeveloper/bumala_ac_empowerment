import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present (works locally, ignored in Render)
load_dotenv()

class Config:
    # General
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///farmer360.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
