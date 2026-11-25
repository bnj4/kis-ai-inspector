from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "KIS AI Inspector"
    database_url: str = "sqlite+aiosqlite:///./kis_inspector.db"
    cors_origins: str = "http://localhost:3000"
    ai_provider: str = "auto"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    github_token: str = ""
    hf_token: str = ""
    internal_api_token: str = ""
    daily_analysis_limit: int = 0
    openai_max_completion_tokens: int = 3000
    request_timeout: int = 20
    max_file_bytes: int = 500000
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
