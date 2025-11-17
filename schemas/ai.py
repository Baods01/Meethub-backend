"""
Coze AI 相关的 Pydantic 数据模型
用于请求和响应的数据验证和序列化
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class MessageContentType(str, Enum):
    """消息内容类型"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    AUDIO = "audio"


class MessageRole(str, Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """消息类型"""
    QUESTION = "question"
    ANSWER = "answer"
    SUGGESTION = "suggestion"


class MessageRequest(BaseModel):
    """单条消息请求"""
    content: str = Field(..., description="消息内容")
    content_type: MessageContentType = Field(
        default=MessageContentType.TEXT,
        description="内容类型"
    )
    role: MessageRole = Field(
        default=MessageRole.USER,
        description="消息角色"
    )
    type: MessageType = Field(
        default=MessageType.QUESTION,
        description="消息类型"
    )


class ChatInitiateRequest(BaseModel):
    """发起对话请求"""
    user_id: str = Field(..., description="用户 ID")
    user_input: str = Field(..., description="用户输入内容")
    conversation_name: str = Field(
        default="Default",
        description="对话名称"
    )
    stream: bool = Field(
        default=False,
        description="是否使用流式响应"
    )
    additional_messages: Optional[List[MessageRequest]] = Field(
        default=None,
        description="额外的消息列表"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="自定义参数"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123456789",
                "user_input": "请帮我推荐一下学术调研活动",
                "conversation_name": "Default",
                "stream": False,
            }
        }


class ChatRetrieveRequest(BaseModel):
    """获取对话详情请求"""
    conversation_id: str = Field(..., description="对话 ID")
    chat_id: str = Field(..., description="聊天消息 ID")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123456789",
                "chat_id": "chat_123456789",
            }
        }


class ChatCancelRequest(BaseModel):
    """取消对话请求"""
    conversation_id: str = Field(..., description="对话 ID")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123456789"
            }
        }


class ChatResponse(BaseModel):
    """对话响应"""
    conversation_id: str = Field(..., description="对话 ID")
    chat_id: str = Field(..., description="聊天消息 ID")
    created_at: Optional[int] = Field(None, description="创建时间戳")
    updated_at: Optional[int] = Field(None, description="更新时间戳")
    status: Optional[str] = Field(None, description="对话状态")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123456789",
                "chat_id": "chat_123456789",
                "created_at": 1700000000,
                "updated_at": 1700000000,
                "status": "completed",
            }
        }


class ChatMessage(BaseModel):
    """聊天消息"""
    id: str = Field(..., description="消息 ID")
    content: str = Field(..., description="消息内容")
    content_type: MessageContentType = Field(..., description="内容类型")
    role: MessageRole = Field(..., description="消息角色")
    created_at: int = Field(..., description="创建时间戳")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg_123456789",
                "content": "我可以为您推荐以下活动...",
                "content_type": "text",
                "role": "assistant",
                "created_at": 1700000000,
            }
        }


class ChatDetailResponse(BaseModel):
    """对话详情响应"""
    conversation_id: str = Field(..., description="对话 ID")
    chat_id: str = Field(..., description="聊天消息 ID")
    messages: List[ChatMessage] = Field(..., description="消息列表")
    status: Optional[str] = Field(None, description="对话状态")
    created_at: Optional[int] = Field(None, description="创建时间戳")
    updated_at: Optional[int] = Field(None, description="更新时间戳")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123456789",
                "chat_id": "chat_123456789",
                "messages": [
                    {
                        "id": "msg_1",
                        "content": "请帮我推荐一下学术调研活动",
                        "content_type": "text",
                        "role": "user",
                        "created_at": 1700000000,
                    },
                    {
                        "id": "msg_2",
                        "content": "我可以为您推荐以下活动...",
                        "content_type": "text",
                        "role": "assistant",
                        "created_at": 1700000001,
                    }
                ],
                "status": "completed",
                "created_at": 1700000000,
                "updated_at": 1700000001,
            }
        }


class CancelChatResponse(BaseModel):
    """取消对话响应"""
    conversation_id: str = Field(..., description="对话 ID")
    status: str = Field(..., description="取消状态")
    message: Optional[str] = Field(None, description="响应消息")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123456789",
                "status": "cancelled",
                "message": "对话已取消",
            }
        }


class RecommendationRequest(BaseModel):
    """推荐请求（高级功能）"""
    user_id: str = Field(..., description="用户 ID")
    user_input: str = Field(..., description="推荐需求描述")
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="额外的上下文信息，如用户偏好、已参加活动等"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123456789",
                "user_input": "我对学术调研感兴趣",
                "context": {
                    "user_interests": ["学术", "调研"],
                    "grade": "大一",
                }
            }
        }


class RecommendationResponse(BaseModel):
    """推荐响应"""
    conversation_id: str = Field(..., description="对话 ID")
    chat_id: str = Field(..., description="聊天消息 ID")
    recommendations: List[Dict[str, Any]] = Field(
        ...,
        description="推荐的活动列表"
    )
    explanation: Optional[str] = Field(
        None,
        description="推荐的原因说明"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123456789",
                "chat_id": "chat_123456789",
                "recommendations": [
                    {
                        "activity_id": "act_1",
                        "name": "学术调研交流会",
                        "score": 0.95,
                    },
                    {
                        "activity_id": "act_2",
                        "name": "科研经验分享",
                        "score": 0.87,
                    }
                ],
                "explanation": "基于您的兴趣，推荐学术相关的活动",
            }
        }
