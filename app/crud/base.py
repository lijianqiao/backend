"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: base.py
@DateTime: 2025-12-30 12:10:00
@Docs: 通用 CRUD 仓库基类 (Generic CRUD Repository) - 支持软删除。
"""

from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base, SoftDeleteMixin

# 定义泛型变量
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase[ModelType: Base, CreateSchemaType: BaseModel, UpdateSchemaType: BaseModel]:
    """
    拥有默认 CRUD 操作的基类。
    支持软删除和乐观锁。

    Attributes:
        model (Type[ModelType]): SQLAlchemy 模型类。
    """

    def __init__(self, model: type[ModelType]):
        """
        CRUD 对象初始化。

        Args:
            model (Type[ModelType]): SQLAlchemy 模型类。
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """
        通过 ID 获取单个记录。
        """
        # 构建查询
        query = select(self.model).where(self.model.id == id)  # pyright: ignore[reportAttributeAccessIssue]

        # 如果模型支持软删除，过滤掉已删除的
        if issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.is_deleted.is_(False))

        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """
        获取多条记录 (分页)。
        """
        query = select(self.model)

        # 软删除过滤
        if issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.is_deleted.is_(False))

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        创建新记录。
        """
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """
        更新记录。
        """
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_data[field])

        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> ModelType | None:
        """
        删除记录 (优先软删除，否则硬删除)。
        """
        obj = await self.get(db, id=id)
        if obj:
            # 使用 isinstance 检查 Mixin，以实现更好的类型安全
            if isinstance(obj, SoftDeleteMixin):
                # 软删除
                obj.is_deleted = True

                db.add(obj)
            else:
                # 硬删除
                await db.delete(obj)

            await db.flush()
        return obj
