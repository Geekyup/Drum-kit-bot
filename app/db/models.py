import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PostStatus(str, enum.Enum):
    pending = "pending"
    published = "published"
    rejected = "rejected"


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("source_channel", "message_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source_channel: Mapped[int] = mapped_column(BigInteger)
    message_id: Mapped[int] = mapped_column(BigInteger)
    message_ids: Mapped[list[int]] = mapped_column(JSON, default=list)
    grouped_id: Mapped[int | None] = mapped_column(BigInteger)
    original_text: Mapped[str] = mapped_column(Text, default="")
    text_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    file_hash: Mapped[str | None] = mapped_column(String(128), index=True)
    draft_text: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(16), default=PostStatus.pending.value, index=True)
    bot_message_id: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
