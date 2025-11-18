"""
Coze AI 智能体路由
提供 AI 相关的接口服务
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Optional
from schemas.ai import (
    ChatInitiateRequest,
    ChatStartResponse,
    ChatRetrieveResponse,
    ChatMessage,
    AiCallResponse,
)
from core.middleware.auth_middleware import JWTAuthMiddleware
from core.permission_checker import requires_permissions
from core.permissions import AI_ASSISTANT_USE
from core.ai.service import coze_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
    dependencies=[Depends(JWTAuthMiddleware())]
)


@router.post(
    "/chat",
    response_model=AiCallResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[requires_permissions([AI_ASSISTANT_USE])]
)
async def call_ai_bot(
    request: Request,
    chat_request: ChatInitiateRequest
):
    """
    非流式调用 Coze AI 智能体

    完整流程：
    1. 发起对话 - 向 AI 智能体发送用户问题
    2. 查看对话详情 - 检查智能体是否完成回答
    3. 查看对话消息详情 - 获取智能体的完整回答

    Args:
        chat_request: 对话请求，包含用户 ID 和输入问题

    Returns:
        AiCallResponse: 包含对话 ID、用户问题、AI 回答、消息列表等信息

    Raises:
        HTTPException: 当调用失败时返回错误信息
    """
    try:
        # 获取当前用户信息
        current_user = request.state.user

        logger.info(
            f"用户 {current_user.id}({current_user.username}) 调用 AI 智能体"
        )

        # 使用当前用户的 ID 作为 user_id
        user_id = str(current_user.id)

        # 调用 AI 服务的完整流程
        result = await coze_service.call_ai_bot(
            user_id=user_id,
            user_input=chat_request.user_input,
        )

        logger.info(
            f"用户 {current_user.id} 的 AI 调用完成，chat_id={result.get('chat_id')}"
        )

        return AiCallResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI 智能体调用失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 智能体调用失败: {str(e)}"
        )


@router.post(
    "/chat/start",
    response_model=ChatStartResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[requires_permissions([AI_ASSISTANT_USE])]
)
async def start_chat(
    request: Request,
    chat_request: ChatInitiateRequest
):
    """
    发起对话请求

    直接发起一个对话，不自动查询结果。如需完整结果，请使用 /ai/chat 接口。

    Args:
        chat_request: 对话请求

    Returns:
        ChatStartResponse: 对话响应，包含 chat_id、conversation_id 等
    """
    try:
        current_user = request.state.user
        user_id = str(current_user.id)

        logger.info(f"用户 {current_user.id} 发起对话")

        response = await coze_service.initiate_conversation(
            user_id=user_id,
            user_input=chat_request.user_input,
            conversation_id=chat_request.conversation_id,
        )

        return ChatStartResponse(**response)

    except Exception as e:
        logger.error(f"发起对话失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发起对话失败: {str(e)}"
        )


@router.get(
    "/chat/{chat_id}/{conversation_id}",
    response_model=ChatRetrieveResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[requires_permissions([AI_ASSISTANT_USE])]
)
async def get_chat_details(
    request: Request,
    chat_id: str,
    conversation_id: str
):
    """
    获取对话详情

    查询指定对话的详情信息，包括状态、创建时间、使用统计等。

    Args:
        chat_id: 聊天消息 ID
        conversation_id: 对话 ID

    Returns:
        ChatRetrieveResponse: 对话详情信息
    """
    try:
        logger.info(
            f"获取对话详情: chat_id={chat_id}, conversation_id={conversation_id}"
        )

        response = await coze_service.get_conversation_details(
            conversation_id=conversation_id,
            chat_id=chat_id,
        )

        return ChatRetrieveResponse(**response)

    except Exception as e:
        logger.error(f"获取对话详情失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取对话详情失败: {str(e)}"
        )


@router.get(
    "/chat/{chat_id}/{conversation_id}/messages",
    response_model=list[ChatMessage],
    status_code=status.HTTP_200_OK,
    dependencies=[requires_permissions([AI_ASSISTANT_USE])]
)
async def get_chat_messages(
    request: Request,
    chat_id: str,
    conversation_id: str
):
    """
    获取对话消息列表

    查询指定对话的所有消息，包括用户问题和 AI 的各个回答步骤。

    Args:
        chat_id: 聊天消息 ID
        conversation_id: 对话 ID

    Returns:
        list[ChatMessage]: 消息列表
    """
    try:
        logger.info(
            f"获取对话消息: chat_id={chat_id}, conversation_id={conversation_id}"
        )

        messages = await coze_service.get_chat_messages(
            conversation_id=conversation_id,
            chat_id=chat_id,
        )

        return [ChatMessage(**msg) for msg in messages]

    except Exception as e:
        logger.error(f"获取对话消息失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取对话消息失败: {str(e)}"
        )
