"""
Coze AI 相关的 Pydantic 数据模型
用于请求和响应的数据验证和序列化
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class ChatInitiateRequest(BaseModel):
    """发起对话请求"""
    user_id: str = Field(..., description="用户 ID")
    user_input: str = Field(..., description="用户输入内容")
    conversation_id: Optional[str] = Field(
        None,
        description="对话 ID（可选，为空则创建新对话）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123456789",
                "user_input": "请帮我推荐一下学术调研活动",
            }
        }


class UsageInfo(BaseModel):
    """API 使用统计信息"""
    token_count: Optional[int] = Field(None, description="总 token 数")
    input_count: Optional[int] = Field(None, description="输入 token 数")
    output_count: Optional[int] = Field(None, description="输出 token 数")


class ChatStartResponse(BaseModel):
    """发起对话响应"""
    id: str = Field(..., description="聊天消息 ID (chat_id)")
    conversation_id: str = Field(..., description="对话 ID")
    bot_id: str = Field(..., description="机器人 ID")
    user_id: Optional[str] = Field(None, description="用户 ID")
    status: str = Field(..., description="对话状态 (completed/processing)")
    created_at: Optional[int] = Field(None, description="创建时间戳")
    completed_at: Optional[int] = Field(None, description="完成时间戳")
    usage: Optional[UsageInfo] = Field(None, description="使用统计信息")
    last_error: Optional[str] = Field(None, description="最后一次错误信息")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "738216760624714****",
                "conversation_id": "738216760624714****",
                "bot_id": "7569792114469879835",
                "status": "completed",
                "created_at": 1718609571,
                "completed_at": 1718609575,
                "usage": {
                    "token_count": 298,
                    "input_count": 242,
                    "output_count": 56,
                }
            }
        }


class ChatRetrieveResponse(BaseModel):
    """获取对话详情响应"""
    id: str = Field(..., description="聊天消息 ID (chat_id)")
    conversation_id: str = Field(..., description="对话 ID")
    bot_id: str = Field(..., description="机器人 ID")
    status: str = Field(..., description="对话状态")
    created_at: Optional[int] = Field(None, description="创建时间戳")
    completed_at: Optional[int] = Field(None, description="完成时间戳")
    usage: Optional[UsageInfo] = Field(None, description="使用统计信息")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "738137187639794****",
                "conversation_id": "738137187639794****",
                "bot_id": "737946218936519****",
                "status": "completed",
                "created_at": 1718609571,
                "completed_at": 1718609575,
                "usage": {
                    "token_count": 298,
                    "input_count": 242,
                    "output_count": 56,
                }
            }
        }


class ChatMessage(BaseModel):
    """聊天消息"""
    id: str = Field(..., description="消息 ID")
    content: str = Field(..., description="消息内容")
    content_type: str = Field(..., description="内容类型 (text/image/file)")
    role: str = Field(..., description="消息角色 (user/assistant)")
    type: Optional[str] = Field(None, description="消息类型 (answer/verbose)")
    bot_id: Optional[str] = Field(None, description="机器人 ID")
    chat_id: Optional[str] = Field(None, description="聊天消息 ID")
    conversation_id: Optional[str] = Field(None, description="对话 ID")
    created_at: Optional[int] = Field(None, description="创建时间戳")
    updated_at: Optional[int] = Field(None, description="更新时间戳")
    reasoning_content: Optional[str] = Field(None, description="推理内容（可选）")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "738216760624724****",
                "content": "2024 年 10 月 1 日是星期二。您可以通过日历或者相关的日期查询工具来核实确认。",
                "content_type": "text",
                "role": "assistant",
                "type": "answer",
                "bot_id": "7379462189365198898",
                "conversation_id": "738147352534297****",
            }
        }


class AiCallResponse(BaseModel):
    """AI 非流式调用响应（完整的问答流程）"""
    conversation_id: str = Field(..., description="对话 ID")
    chat_id: str = Field(..., description="聊天消息 ID")
    user_input: str = Field(..., description="用户输入的问题")
    ai_response: Optional[str] = Field(None, description="AI 智能体的回答")
    status: str = Field(..., description="对话状态")
    messages: List[ChatMessage] = Field(..., description="所有消息列表")
    usage: Optional[UsageInfo] = Field(None, description="使用统计信息")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "738216760624714****",
                "chat_id": "738216760624714****",
                "user_input": "2024 年 10 月 1 日是星期几？",
                "ai_response": "2024 年 10 月 1 日是星期二。您可以通过日历或者相关的日期查询工具来核实确认。",
                "status": "completed",
                "messages": [
                    {
                        "id": "msg_1",
                        "content": "2024 年 10 月 1 日是星期几？",
                        "content_type": "text",
                        "role": "user",
                        "type": "question",
                    },
                    {
                        "id": "msg_2",
                        "content": "2024 年 10 月 1 日是星期二...",
                        "content_type": "text",
                        "role": "assistant",
                        "type": "answer",
                    }
                ],
                "usage": {
                    "token_count": 298,
                    "input_count": 242,
                    "output_count": 56,
                }
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


class CancelChatResponse(BaseModel):
    """取消对话响应"""
    conversation_id: str = Field(..., description="对话 ID")
    status: Optional[str] = Field(None, description="取消状态")
    message: Optional[str] = Field(None, description="响应消息")
