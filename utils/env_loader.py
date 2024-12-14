import os
from dotenv import load_dotenv

def load_env(file_path="config/.env"):
    """
    Loads environment variables from the specified .env file.
    :param file_path: Path to the .env file.
    :return: None
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f".env file not found: {file_path}")
    load_dotenv(dotenv_path=file_path)
