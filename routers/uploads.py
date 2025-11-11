import os
from typing import Optional

from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException, status, Depends
from core.middleware.auth_middleware import JWTAuthMiddleware
from dao.activity_dao import ActivityDAO
from schemas.uploads import UploadImageResponse


router = APIRouter(
    prefix="/uploads",
    tags=["文件"],
    dependencies=[Depends(JWTAuthMiddleware())]
)


# 计算 TopActivities 静态目录（相对于 routers 目录）
TOP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "img", "TopActivities"))
os.makedirs(TOP_DIR, exist_ok=True)

activity_dao = ActivityDAO()


@router.post("/images/activities/cover", response_model=UploadImageResponse)
async def upload_activity_cover(
    activity_id: int = Form(...),
    file: UploadFile = File(...),
    request: Request = None
):
    """上传活动封面图：仅允许活动发布者调用。

    请求格式：multipart/form-data，包含字段 `activity_id`(form) 和 `file`(file)
    """

    # 从中间件注入的 request.state.user 获取当前用户
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证的用户"
        )

    # 获取活动并校验
    activity = await activity_dao.get_by_id(activity_id)
    if not activity or getattr(activity, "is_deleted", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到ID为 {activity_id} 的活动"
        )

    # 检查发布者：使用外键 publisher_id（Tortoise 会保存该属性）
    publisher_id = getattr(activity, "publisher_id", None)
    # 如果 publisher_id 为空，尝试加载关联
    if publisher_id is None:
        try:
            await activity.fetch_related('publisher')
            publisher_id = getattr(activity, "publisher_id", None)
        except Exception:
            publisher_id = None

    if publisher_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有活动发布者可以上传封面图"
        )

    # 保存文件（以活动ID命名，保留原始扩展名）
    original_filename = getattr(file, "filename", "")
    _, ext = os.path.splitext(original_filename)
    if not ext:
        ext = ".jpg"

    filename = f"{activity_id}{ext}"
    filepath = os.path.join(TOP_DIR, filename)

    try:
        content = await file.read()
        with open(filepath, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存文件时出错: {str(e)}"
        )

    # 构建完整的 cover_image URL
    base_url = f"http://{request.client.host}:{request.url.port}" if request.url.port else f"http://{request.client.host}"
    cover_image_url = f"{base_url}/static/img/TopActivities/{filename}"
    
    # 更新活动的 cover_image 字段为完整的 URL
    updated = await activity_dao.update(activity_id, cover_image=cover_image_url)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新活动封面字段失败"
        )

    # 获取更新后的活动完整信息（包含发布者）
    updated_full = await activity_dao.get_activity_with_stats(activity_id)

    # 构建简单的活动字典作为响应（避免直接返回 ORM 对象）
    activity_dict = {
        "id": updated_full.id,
        "title": updated_full.title,
        "description": updated_full.description,
        "cover_image": updated_full.cover_image,
        "location": updated_full.location,
        "start_time": updated_full.start_time,
        "end_time": updated_full.end_time,
        "max_participants": updated_full.max_participants,
        "current_participants": updated_full.current_participants,
        "tags": updated_full.tags,
        "target_audience": updated_full.target_audience,
        "benefits": updated_full.benefits,
        "status": updated_full.status,
        "views_count": updated_full.views_count,
        "is_deleted": updated_full.is_deleted,
        "created_at": updated_full.created_at,
        "updated_at": updated_full.updated_at,
        "publisher": {"id": getattr(updated_full, "publisher_id", None)}
    }

    return {
        "success": True,
        "filename": filename,
        "activity": activity_dict
    }
