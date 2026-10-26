from telethon import TelegramClient
from telethon.sessions import StringSession

from app.config import settings

client = TelegramClient(StringSession(settings.tg_session), settings.tg_api_id, settings.tg_api_hash)
