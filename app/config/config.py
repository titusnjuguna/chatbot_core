from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

 

class Settings(BaseSettings):
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY")
    upload_dir: Path = Path("./uploads")
    chroma_persist_dir: Path = Path("./chroma_db")
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Ensure directories exist
settings.upload_dir.mkdir(exist_ok=True)
settings.chroma_persist_dir.mkdir(exist_ok=True)