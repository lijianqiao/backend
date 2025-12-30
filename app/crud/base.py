"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: base.py
@DateTime: 2025-12-30 12:10:00
@Docs: 通用 CRUD 仓库基类 (Generic CRUD Repository).
"""

from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

# 定义泛型变量
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase[ModelType: Base, CreateSchemaType: BaseModel, UpdateSchemaType: BaseModel]:
    """
    拥有默认 CRUD 操作的基类。

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

        Args:
            db (AsyncSession): 数据库会话。
            id (Any): 主键 ID。

        Returns:
            Optional[ModelType]: 找到的记录或 None。
        """
        # 注意: 如果 Pylance 报错 Base 没有 id 属性，这是因为 Mixin 的动态性。
        # 我们可以忽略此错误，或者在 Base 中显式声明 (已在 base.py 做了 Mixin)。
        # 这里使用 getattr 或 显式 where 子句通常没问题。
        # self.model.id 是由 DeclarativeBase 提供的。
        query = select(self.model).where(self.model.id == id)  # type: ignore
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """
        获取多条记录 (分页)。

        Args:
            db (AsyncSession): 数据库会话。
            skip (int): 跳过的记录数。
            limit (int): 返回的最大记录数。

        Returns:
            List[ModelType]: 记录列表。
        """
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        创建新记录。

        Args:
            db (AsyncSession): 数据库会话。
            obj_in (CreateSchemaType): 创建数据的 Schema 对象。

        Returns:
            ModelType: 创建后的数据库对象。
        """
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """
        更新记录。

        Args:
            db (AsyncSession): 数据库会话。
            db_obj (ModelType): 待更新的数据库对象。
            obj_in (Union[UpdateSchemaType, Dict[str, Any]]): 更新数据的 Schema 或 字典。

        Returns:
            ModelType: 更新后的数据库对象。
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
        删除记录 (硬删除)。

        Args:
            db (AsyncSession): 数据库会话。
            id (Any): 主键 ID。

        Returns:
            ModelType | None: 被删除的对象。
        """
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.flush()
        return obj
