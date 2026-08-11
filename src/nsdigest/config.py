from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    dropbox_app_key: str
    dropbox_app_secret: str
    dropbox_refresh_token: str

    dropbox_root: str = ""

    news_user_agent: str = "NS-Digest/0.1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
