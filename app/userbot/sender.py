from collections.abc import Sequence

from telethon import TelegramClient


async def send_to_bot(client: TelegramClient, bot_username: str, post_id: int, messages: Sequence) -> None:
    media = [m.media for m in messages if m.photo or m.document]
    marker = f"#{post_id}"
    if media:
        captions = [marker] + [""] * (len(media) - 1)
        await client.send_file(bot_username, media, caption=captions)
    else:
        await client.send_message(bot_username, marker)
