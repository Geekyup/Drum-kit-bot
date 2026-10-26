import asyncio
import logging
import re

from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy import update

from app.bot.callbacks import DraftAction
from app.bot.keyboards import draft_kb
from app.bot.posting import extract_media, send_post
from app.config import settings
from app.db.models import Post, PostStatus
from app.db.session import session_factory

log = logging.getLogger(__name__)

router = Router()

MARKER_RE = re.compile(r"^#(\d+)")
ALBUM_WAIT = 1.5

buffers: dict[str, list[Message]] = {}


@router.message(CommandStart())
async def start(message: Message) -> None:
    if message.from_user and message.from_user.id == settings.owner_id:
        await message.answer("Предложка активна")


@router.callback_query(DraftAction.filter())
async def on_action(query: CallbackQuery, callback_data: DraftAction, bot: Bot) -> None:
    if query.from_user.id != settings.owner_id:
        await query.answer()
        return

    publish = callback_data.action == "publish"
    new_status = PostStatus.published.value if publish else PostStatus.rejected.value

    async with session_factory() as session:
        result = await session.execute(
            update(Post)
            .where(Post.id == callback_data.post_id, Post.status == PostStatus.pending.value)
            .values(status=new_status)
        )
        await session.commit()
        if result.rowcount == 0:
            await query.answer("Уже обработан")
            return
        post = await session.get(Post, callback_data.post_id)

    if publish:
        try:
            await send_post(bot, settings.target_channel, post.media or [], post.draft_text)
        except Exception:
            log.exception("publish failed for post %s", post.id)
            async with session_factory() as session:
                await session.execute(
                    update(Post).where(Post.id == post.id).values(status=PostStatus.pending.value)
                )
                await session.commit()
            await query.answer("Ошибка публикации, смотри логи", show_alert=True)
            return

    label = "✅ Опубликовано" if publish else "❌ Отклонено"
    await query.message.edit_text(f"Пост #{post.id}: {label}")
    await query.answer()


@router.message()
async def from_userbot(message: Message, bot: Bot, userbot_id: int) -> None:
    if not message.from_user or message.from_user.id != userbot_id:
        return

    key = message.media_group_id or f"s{message.message_id}"
    group = buffers.get(key)
    if group is not None:
        group.append(message)
        return

    buffers[key] = [message]
    if message.media_group_id:
        await asyncio.sleep(ALBUM_WAIT)
    messages = buffers.pop(key)

    try:
        await deliver(bot, messages)
    except Exception:
        log.exception("deliver failed")


async def deliver(bot: Bot, messages: list[Message]) -> None:
    messages = sorted(messages, key=lambda m: m.message_id)

    post_id = None
    for message in messages:
        found = MARKER_RE.match(message.caption or message.text or "")
        if found:
            post_id = int(found.group(1))
            break
    if post_id is None:
        log.warning("marker not found, skipping group")
        return

    media = [item for item in (extract_media(m) for m in messages) if item]

    async with session_factory() as session:
        post = await session.get(Post, post_id)
        if post is None or post.media is not None:
            return
        post.media = media
        post.draft_text = post.original_text.strip()
        await session.commit()

    await send_post(bot, settings.owner_id, media, post.draft_text)
    control = await bot.send_message(settings.owner_id, f"Пост #{post.id}", reply_markup=draft_kb(post.id))

    async with session_factory() as session:
        await session.execute(update(Post).where(Post.id == post.id).values(bot_message_id=control.message_id))
        await session.commit()
