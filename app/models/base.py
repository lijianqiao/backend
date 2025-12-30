"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: base.py
@DateTime: 2025-12-30 11:41:00
@Docs: Base model definition with UUIDv7 and audit timestamps.
"""

import uuid
from datetime import datetime

import uuid6
from sqlalchemy import Boolean, DateTime, MetaData, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

# Recommended naming convention for constraints
meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class Base(DeclarativeBase):
    metadata = meta


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid6.uuid7,
        server_default=func.gen_random_uuid(),  # Postgres has this, or we can rely on app-side generation. uuid7 is better generated app side usually or via specific pg extension. Let's rely on app-side default for uuid7 logic consistency.
        unique=True,
        index=True,
        nullable=False,
    )


class VersionMixin:
    version_id: Mapped[str] = mapped_column(
        String, default=lambda: uuid.uuid4().hex, onupdate=lambda: uuid.uuid4().hex, nullable=False
    )


class AuditableModel(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, VersionMixin):
    """
    Abstract base model that includes:
    - UUIDv7 Primary Key
    - Created/Updated timestamps
    - Soft delete flag
    - Optimistic locking version
    """

    __abstract__ = True

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
