# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite:///./insightflow.db"  # 冲刺期先用 SQLite，稳定后切 Postgres
    llm_provider: str = "deepseek"   # deepseek | ollama，改这里即可切换
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"  

settings = Settings()