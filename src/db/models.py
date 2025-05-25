import uuid
from typing import List

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class User(Base):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
        sort_order=-10,
    )
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str | None] = mapped_column(unique=True)
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    hashed_password: Mapped[str]

    jwt_tokens: Mapped[List["JwtToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class JwtToken(Base):
    id: Mapped[str] = mapped_column(primary_key=True)
    token_type: Mapped[str]
    email: Mapped[str] = mapped_column(
        ForeignKey("users.email", ondelete="CASCADE")
    )
    device_id: Mapped[str | None]
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(
        back_populates="jwt_tokens", passive_deletes=True, single_parent=True
    )
