import hashlib
import re

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Post

NOISE_URL_RE = re.compile(r"https?://\S+|t\.me/\S+|@\w+")
PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)


def normalize(text: str) -> str:
    text = NOISE_URL_RE.sub(" ", text.lower())
    text = PUNCT_RE.sub(" ", text)
    return " ".join(text.split())


def text_hash(text: str) -> str | None:
    normalized = normalize(text)
    if len(normalized) < 20:
        return None
    return hashlib.sha256(normalized.encode()).hexdigest()


async def is_duplicate(session: AsyncSession, th: str | None, fh: str | None) -> bool:
    conditions = []
    if th:
        conditions.append(Post.text_hash == th)
    if fh:
        conditions.append(Post.file_hash == fh)
    if not conditions:
        return False
    result = await session.execute(select(Post.id).where(or_(*conditions)).limit(1))
    return result.first() is not None
