import asyncio
import logging
from collections.abc import Sequence

from aiogram import Bot, Dispatcher

from app.bot.handlers import router
from app.config import settings
from app.db.session import init_db
from app.userbot.client import client
from app.userbot.listener import register
from app.userbot.sender import send_to_bot

log = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    await init_db()

    await client.connect()
    if not await client.is_user_authorized():
        raise RuntimeError("TG_SESSION невалидна, перегенерируй через scripts/login_userbot.py")
    me = await client.get_me()

    bot = Bot(settings.bot_token)
    bot_username = (await bot.get_me()).username

    dp = Dispatcher()
    dp.include_router(router)
    dp["userbot_id"] = me.id

    async def on_saved(post_id: int, messages: Sequence) -> None:
        log.info("saved post %s", post_id)
        await send_to_bot(client, bot_username, post_id, messages)

    register(client, on_saved)
    log.info("started, userbot=%s bot=@%s", me.id, bot_username)

    try:
        await asyncio.gather(dp.start_polling(bot), client.run_until_disconnected())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
