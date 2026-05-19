from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="AURALIS_", env_file=".env", extra="ignore")

    window_seconds: int = 30
    redis_url: str | None = None
    sentiment_model: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    enable_transformers: bool = False
    twitch_channel: str | None = None
    twitch_nick: str | None = None
    twitch_token: str | None = None
    youtube_video_id: str | None = None
