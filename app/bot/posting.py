from aiogram import Bot
from aiogram.types import InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo, Message

CAPTION_LIMIT = 1024
TEXT_LIMIT = 4096

SEND_METHODS = {
    "photo": "send_photo",
    "video": "send_video",
    "audio": "send_audio",
    "document": "send_document",
}

INPUT_MEDIA = {
    "photo": InputMediaPhoto,
    "video": InputMediaVideo,
    "audio": InputMediaAudio,
    "document": InputMediaDocument,
}


def extract_media(message: Message) -> dict | None:
    if message.photo:
        return {"type": "photo", "file_id": message.photo[-1].file_id}
    if message.video:
        return {"type": "video", "file_id": message.video.file_id}
    if message.audio:
        return {"type": "audio", "file_id": message.audio.file_id}
    if message.document:
        return {"type": "document", "file_id": message.document.file_id}
    return None


async def send_post(bot: Bot, chat_id: int, media: list[dict], text: str) -> list[int]:
    text = text.strip()
    ids: list[int] = []
    if not media:
        message = await bot.send_message(chat_id, text[:TEXT_LIMIT])
        return [message.message_id]

    caption = text if text and len(text) <= CAPTION_LIMIT else None

    if len(media) == 1:
        item = media[0]
        sender = getattr(bot, SEND_METHODS[item["type"]])
        message = await sender(chat_id, item["file_id"], caption=caption)
        ids.append(message.message_id)
    else:
        group = [
            INPUT_MEDIA[item["type"]](media=item["file_id"], caption=caption if index == 0 else None)
            for index, item in enumerate(media)
        ]
        messages = await bot.send_media_group(chat_id, group)
        ids.extend(m.message_id for m in messages)

    if text and caption is None:
        message = await bot.send_message(chat_id, text[:TEXT_LIMIT])
        ids.append(message.message_id)
    return ids
