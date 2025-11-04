from typing import TypeVar, Generic, Type, Optional, List
from tortoise import Model
from tortoise.exceptions import DoesNotExist

ModelType = TypeVar("ModelType", bound=Model)

class BaseDAO(Generic[ModelType]):
    """基础数据访问对象类"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, **kwargs) -> ModelType:
        """创建记录"""
        return await self.model.create(**kwargs)

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """通过ID获取记录"""
        try:
            return await self.model.get(id=id)
        except DoesNotExist:
            return None

    async def get_all(self) -> List[ModelType]:
        """获取所有记录"""
        return await self.model.all()

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """更新记录"""
        try:
            obj = await self.model.get(id=id)
            await obj.update_from_dict(kwargs).save()
            return obj
        except DoesNotExist:
            return None

    async def delete(self, id: int) -> bool:
        """删除记录"""
        count = await self.model.filter(id=id).delete()
        return count > 0