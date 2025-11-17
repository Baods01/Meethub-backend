from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from datetime import datetime, timedelta
from schemas.activities import (
    ActivityCreate, ActivityInDB, ActivityStats, ActivityUpdate,
    ActivityList, ActivitySearch
)
from dao.activity_dao import ActivityDAO
from core.permission_checker import requires_permissions
from core.middleware.auth_middleware import JWTAuthMiddleware
from core.middleware.logging_middleware import operation_logger
from core.permissions import ACTIVITY_UPDATE, ACTIVITY_DELETE
from fastapi.security import HTTPBearer
from typing import List, Dict, Optional
from tortoise.expressions import Q

router = APIRouter(
    prefix="/activities",
    tags=["活动"],
    dependencies=[Depends(JWTAuthMiddleware())]
)

activity_dao = ActivityDAO()

@router.get(
    "/organizer/my-activities",
    response_model=ActivityList,
    status_code=status.HTTP_200_OK,
    dependencies=[requires_permissions(["activity:list"])]
)
async def get_organizer_activities(
    request: Request,
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100)
):
    """
    获取组织者的活动列表
    - 需要活动列表查看权限
    - 返回当前用户发布的所有活动详细信息
    - 支持分页
    
    此接口用于活动组织者查看自己发布的所有活动，包括草稿、已发布、进行中、已结束等所有状态的活动。
    """
    try:
        # 从请求状态中获取当前用户（组织者）信息
        organizer_id = request.state.user.id
        
        # 查询该用户发布的所有活动
        from models.activities import Activities
        query = Activities.filter(publisher_id=organizer_id, is_deleted=False)
        
        # 统计总数
        total = await query.count()
        
        # 分页和排序
        activities = await query.order_by('-created_at')\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .prefetch_related('publisher')
        
        return ActivityList(
            total=total,
            items=activities,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取组织者活动列表失败: {str(e)}"
        )

@router.get(
    "/search",
    response_model=ActivityList,
    status_code=status.HTTP_200_OK,
    dependencies=[requires_permissions(["activity:read"])]
)
async def search_activities(
    request: Request,
    keyword: Optional[str] = None,
    benefits: Optional[List[str]] = Query(None),
    time_range: str = Query(None, regex="^(this_week|two_weeks|one_month)$"),
    targeted_people: Optional[List[str]] = Query(None),
    activity_class: Optional[List[str]] = Query(None),
    sort_by: Optional[str] = Query(
        None,
        description="排序字段：前缀'-'表示倒序",
        regex="^(-?created_at|-?views_count|-?current_participants|-?start_time)$"
    ),
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100)
):
    """
    搜索活动
    - 支持多条件组合查询
    - 支持分页
    - 支持排序

    时间范围选项:
    - this_week: 本周内
    - two_weeks: 两周内
    - one_month: 一个月内

    排序选项（前缀'-'表示倒序）:
    - created_at/-created_at: 按创建时间排序
    - views_count/-views_count: 按浏览量排序
    - current_participants/-current_participants: 按当前参与人数排序
    - start_time/-start_time: 按开始时间排序
    """
    try:
        # 处理时间范围
        now = datetime.now()
        time_filter = None
        if time_range:
            if time_range == "this_week":
                time_filter = {"start": now - timedelta(days=now.weekday()), "end": now + timedelta(days=6-now.weekday())}
            elif time_range == "two_weeks":
                time_filter = {"start": now - timedelta(weeks=2), "end": now}
            elif time_range == "one_month":
                time_filter = {"start": now - timedelta(days=30), "end": now}

        # 构建受众群体筛选条件
        audience = {}
        if targeted_people:
            audience["Targeted_people"] = targeted_people
        if activity_class:
            audience["Activity_class"] = activity_class

        # 执行搜索
        result = await activity_dao.search_activities(
            keyword=keyword,
            benefits=benefits,
            audience=audience if audience else None,
            time_range=time_filter,
            sort_by=sort_by,
            page=page,
            page_size=page_size
        )

        return ActivityList(
            total=result["total"],
            items=result["items"],
            page=result["page"],
            page_size=result["page_size"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索活动失败: {str(e)}"
        )

@router.post(
    "/",
    response_model=ActivityInDB,
    status_code=status.HTTP_201_CREATED,
    dependencies=[requires_permissions(["activity:publish"])]
)
async def create_activity(
    activity: ActivityCreate,
    request: Request
):
    """
    创建新活动
    - 需要活动发布权限
    - 验证请求数据
    - 保存到数据库
    """
    try:
        # 从请求状态中获取当前用户（发布者）信息
        publisher_id = request.state.user.id  # 通过 JWTAuthMiddleware 注入的用户信息

        # 创建活动
        created_activity = await activity_dao.create_activity(
            data=activity.model_dump(exclude={"publisher"}),
            publisher_id=publisher_id
        )
        
        return created_activity
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建活动失败: {str(e)}"
        )

@router.get(
    "/{activity_id}",
    response_model=Dict,
    status_code=status.HTTP_200_OK
)
async def get_activity_details(
    activity_id: int,
    request: Request
):
    """
    获取活动详情
    - 任何已登录用户可访问
    - 返回活动详细信息和统计数据
    - 发布者信息包含手机号和邮箱
    - 浏览量自动+1
    - 记录用户浏览活动的操作日志
    """
    try:
        # 获取活动详情
        activity = await activity_dao.get_activity_with_stats(activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="活动不存在"
            )

        # 增加浏览量
        await activity_dao.increment_views(activity_id)
        # 更新内存中的活动对象的浏览量
        activity.views_count += 1

        # 记录用户浏览活动的操作日志
        if hasattr(request.state, 'user') and request.state.user:
            await operation_logger.log_activity_view(request, activity_id)

        # 获取活动统计信息
        stats = await activity_dao.get_activity_stats(activity_id)

        # 组合返回数据，使用包含联系方式的发布者信息
        activity_data = ActivityInDB.from_orm(activity).model_dump()
        return {
            "activity": activity_data,
            "stats": stats
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取活动详情失败: {str(e)}"
        )

@router.put(
    "/{activity_id}",
    response_model=ActivityInDB,
    status_code=status.HTTP_200_OK
)
async def update_activity(
    activity_id: int,
    activity_update: ActivityUpdate,
    request: Request
):
    """
    更新活动信息
    - 需要是活动发布者
    - 验证请求数据
    - 更新活动信息
    """
    try:
        # 获取活动信息
        activity = await activity_dao.get_activity_with_stats(activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="活动不存在"
            )

        # 验证用户是否为活动发布者
        current_user_id = request.state.user.id
        if current_user_id != activity.publisher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有活动发布者可以更新活动信息"
            )

        # 更新活动
        update_data = activity_update.model_dump(exclude_unset=True)
        if update_data:
            for key, value in update_data.items():
                setattr(activity, key, value)
            await activity.save()
            # 重新获取更新后的活动信息
            activity = await activity_dao.get_activity_with_stats(activity_id)

        return activity

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新活动失败: {str(e)}"
        )

@router.delete(
    "/{activity_id}",
    response_model=Dict,
    status_code=status.HTTP_200_OK
)
async def delete_activity(
    activity_id: int,
    request: Request
):
    """
    删除活动（软删除）
    - 需要是活动发布者
    - 执行软删除操作
    - 返回删除结果信息
    """
    try:
        # 获取活动信息
        activity = await activity_dao.get_activity_with_stats(activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="活动不存在"
            )

        # 验证用户是否为活动发布者
        current_user_id = request.state.user.id
        if current_user_id != activity.publisher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有活动发布者可以删除活动"
            )

        # 执行软删除
        success = await activity_dao.soft_delete(activity_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除活动失败"
            )

        # 返回成功响应
        return {
            "success": True,
            "message": f"活动 '{activity.title}' 已成功删除",
            "activity_id": activity_id
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除活动失败: {str(e)}"
        )

@router.patch(
    "/{activity_id}/status",
    response_model=ActivityInDB,
    status_code=status.HTTP_200_OK
)
async def update_activity_status(
    request: Request,
    activity_id: int,
    status: str = Query(
        ...,
        description="活动状态",
        regex="^(draft|published|ongoing|ended|cancelled)$"
    )
):
    """
    更新活动状态
    - 需要是活动发布者
    - 更新活动状态
    
    可用状态:
    - draft: 草稿
    - published: 已发布
    - ongoing: 进行中
    - ended: 已结束
    - cancelled: 已取消
    """
    try:
        # 获取活动信息
        activity = await activity_dao.get_activity_with_stats(activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="活动不存在"
            )

        # 验证用户是否为活动发布者
        current_user_id = request.state.user.id
        if current_user_id != activity.publisher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有活动发布者可以更新活动状态"
            )

        # 更新状态
        updated_activity = await activity_dao.update_activity_status(activity_id, status)
        if not updated_activity:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新活动状态失败"
            )

        # 重新获取完整的活动信息
        return await activity_dao.get_activity_with_stats(activity_id)

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新活动状态失败: {str(e)}"
        )