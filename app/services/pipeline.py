import re
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from app.db.models import Post
from app.db.session import session_factory
from app.services.dedup import is_duplicate, text_hash

LINK_RE = re.compile(r"https?://\S+|t\.me/\S+")


@dataclass
class Incoming:
    channel_id: int
    message_ids: list[int]
    grouped_id: int | None
    text: str
    file_hash: str | None
    has_media: bool


def is_candidate(incoming: Incoming) -> bool:
    return incoming.has_media or bool(LINK_RE.search(incoming.text))


async def ingest(incoming: Incoming) -> int | None:
    if not is_candidate(incoming):
        return None
    th = text_hash(incoming.text)
    async with session_factory() as session:
        if await is_duplicate(session, th, incoming.file_hash):
            return None
        post = Post(
            source_channel=incoming.channel_id,
            message_id=min(incoming.message_ids),
            message_ids=sorted(incoming.message_ids),
            grouped_id=incoming.grouped_id,
            original_text=incoming.text,
            text_hash=th,
            file_hash=incoming.file_hash,
        )
        session.add(post)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            return None
        return post.id
