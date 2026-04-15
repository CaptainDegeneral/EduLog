from collections.abc import Sequence
import logging
from typing import Any, Generic, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    model: type[ModelType]

    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(self.__class__.__module__)

    async def create(self, data: dict[str, Any]) -> ModelType:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        self.logger.info("Repository create model=%s id=%s", self.model.__name__, getattr(instance, "id", None))
        return instance

    async def get(self, entity_id: int) -> ModelType | None:
        instance = await self.session.get(self.model, entity_id)
        self.logger.debug(
            "Repository get model=%s id=%s found=%s",
            self.model.__name__,
            entity_id,
            instance is not None,
        )
        return instance

    async def list(self, statement: Select[tuple[ModelType]] | None = None) -> Sequence[ModelType]:
        query = statement if statement is not None else select(self.model)
        result = await self.session.scalars(query)
        items = result.all()
        self.logger.info("Repository list model=%s count=%s", self.model.__name__, len(items))
        return items

    async def update(self, instance: ModelType, data: dict[str, Any]) -> ModelType:
        for field, value in data.items():
            setattr(instance, field, value)

        await self.session.flush()
        await self.session.refresh(instance)
        self.logger.info(
            "Repository update model=%s id=%s fields=%s",
            self.model.__name__,
            getattr(instance, "id", None),
            sorted(data.keys()),
        )
        return instance

    async def delete(self, instance: ModelType) -> None:
        instance_id = getattr(instance, "id", None)
        await self.session.delete(instance)
        await self.session.flush()
        self.logger.info("Repository delete model=%s id=%s", self.model.__name__, instance_id)
