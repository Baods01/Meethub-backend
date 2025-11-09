from pydantic import BaseModel
from typing import Dict, Any


class UploadImageIn(BaseModel):
    """上传图片请求中的表单字段（建议保留用于文档说明）"""
    activity_id: int


class UploadImageResponse(BaseModel):
    success: bool
    filename: str
    activity: Dict[str, Any]
