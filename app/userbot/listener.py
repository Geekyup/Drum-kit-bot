import hashlib
import logging
from collections.abc import Awaitable, Callable, Sequence

from telethon import TelegramClient, events

from app.config import settings
from app.services.pipeline import Incoming, ingest

log = logging.getLogger(__name__)

OnSaved = Callable[[int, Sequence], Awaitable[None]]


def media_key(messages: Sequence) -> str | None:
    ids = []
    for message in messages:
        if message.document:
            ids.append(f"d{message.document.id}")
        elif message.photo:
            ids.append(f"p{message.photo.id}")
    if not ids:
        return None
    return hashlib.sha256(",".join(sorted(ids)).encode()).hexdigest()


def register(client: TelegramClient, on_saved: OnSaved) -> None:
    chats = settings.sources
    if not chats:
        raise RuntimeError("SOURCE_CHANNELS пуст")

    async def handle(chat_id: int, messages: Sequence, grouped_id: int | None, text: str) -> None:
        incoming = Incoming(
            channel_id=chat_id,
            message_ids=[m.id for m in messages],
            grouped_id=grouped_id,
            text=text or "",
            file_hash=media_key(messages),
            has_media=any(m.media for m in messages),
        )
        post_id = await ingest(incoming)
        if post_id is not None:
            await on_saved(post_id, messages)

    @client.on(events.NewMessage(chats=chats, func=lambda e: e.message.grouped_id is None))
    async def on_single(event: events.NewMessage.Event) -> None:
        try:
            await handle(event.chat_id, [event.message], None, event.message.message)
        except Exception:
            log.exception("single message failed")

    @client.on(events.Album(chats=chats))
    async def on_album(event: events.Album.Event) -> None:
        try:
            await handle(event.chat_id, event.messages, event.grouped_id, event.text)
        except Exception:
            log.exception("album failed")
