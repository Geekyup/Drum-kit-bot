from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    tg_api_id: int
    tg_api_hash: str
    tg_session: str
    bot_token: str
    owner_id: int
    target_channel: int
    source_channels: str = ""
    database_url: str = "sqlite+aiosqlite:///data/app.db"
    gemini_api_key: str = ""

    @property
    def sources(self) -> list[int | str]:
        result: list[int | str] = []
        for item in self.source_channels.split(","):
            item = item.strip()
            if not item:
                continue
            result.append(int(item) if item.lstrip("-").isdigit() else item.lstrip("@"))
        return result


settings = Settings()
