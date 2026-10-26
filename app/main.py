import asyncio
import logging

from app.db.session import init_db
from app.userbot.client import client
from app.userbot.listener import register

log = logging.getLogger(__name__)


async def on_saved(post_id: int) -> None:
    log.info("saved post %s", post_id)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    await init_db()
    register(client, on_saved)
    await client.connect()
    if not await client.is_user_authorized():
        raise RuntimeError("TG_SESSION невалидна, перегенерируй через scripts/login_userbot.py")
    log.info("userbot started")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
