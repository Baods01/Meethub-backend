"""
Coze AI 智能体 HTTP 客户端
用于与 Coze API 进行通信
"""
import httpx
import json
from typing import Optional, Dict, Any, AsyncGenerator
from settings import COZE_CONFIG


class CozeClient:
    """
    Coze 智能体客户端
    封装 Coze API 的 HTTP 请求操作
    """

    def __init__(self):
        """初始化 Coze 客户端"""
        self.api_token = COZE_CONFIG['api_token']
        self.api_base_url = COZE_CONFIG['api_base_url']
        self.bot_id = COZE_CONFIG['bot_id']
        self.workflow_id = COZE_CONFIG['workflow_id']
        self.timeout = COZE_CONFIG['timeout']

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    async def start_chat(
        self,
        user_id: str,
        user_input: str,
        conversation_name: str = "Default",
        stream: bool = True,
        additional_messages: Optional[list] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        发起对话请求

        Args:
            user_id: 用户 ID
            user_input: 用户输入内容
            conversation_name: 对话名称
            stream: 是否使用流式响应
            additional_messages: 额外的消息列表
            parameters: 自定义参数

        Returns:
            API 响应字典，包含 conversation_id 和 chat_id
        """
        url = f"{self.api_base_url}/chat"

        # 构建请求体
        payload = {
            "bot_id": self.bot_id,
            "workflow_id": self.workflow_id,
            "user_id": user_id,
            "stream": stream,
            "additional_messages": additional_messages or [],
            "parameters": parameters or {
                "BOT_USER_INPUT": user_input,
                "CONVERSATION_NAME": conversation_name,
            },
        }

        # 如果没有提供 additional_messages，使用默认的问题格式
        if not additional_messages:
            payload["additional_messages"] = [
                {
                    "content": user_input,
                    "content_type": "text",
                    "role": "user",
                    "type": "question",
                }
            ]

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                headers=self._get_headers(),
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def start_chat_stream(
        self,
        user_id: str,
        user_input: str,
        conversation_name: str = "Default",
        additional_messages: Optional[list] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        发起流式对话请求

        Args:
            user_id: 用户 ID
            user_input: 用户输入内容
            conversation_name: 对话名称
            additional_messages: 额外的消息列表
            parameters: 自定义参数

        Yields:
            逐行的响应内容
        """
        url = f"{self.api_base_url}/chat"

        # 构建请求体
        payload = {
            "bot_id": self.bot_id,
            "workflow_id": self.workflow_id,
            "user_id": user_id,
            "stream": True,
            "additional_messages": additional_messages or [],
            "parameters": parameters or {
                "BOT_USER_INPUT": user_input,
                "CONVERSATION_NAME": conversation_name,
            },
        }

        # 如果没有提供 additional_messages，使用默认的问题格式
        if not additional_messages:
            payload["additional_messages"] = [
                {
                    "content": user_input,
                    "content_type": "text",
                    "role": "user",
                    "type": "question",
                }
            ]

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                url,
                headers=self._get_headers(),
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        yield line

    async def retrieve_chat(
        self,
        conversation_id: str,
        chat_id: str,
    ) -> Dict[str, Any]:
        """
        获取对话详情

        Args:
            conversation_id: 对话 ID
            chat_id: 聊天消息 ID

        Returns:
            对话详情数据
        """
        url = f"{self.api_base_url}/chat/retrieve"

        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id,
        }

        payload = {
            "workflow_id": self.workflow_id,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                url,
                headers=self._get_headers(),
                params=params,
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def cancel_chat(
        self,
        conversation_id: str,
    ) -> Dict[str, Any]:
        """
        取消对话/会话

        Args:
            conversation_id: 对话 ID

        Returns:
            取消操作的响应
        """
        url = f"{self.api_base_url}/chat/cancel"

        payload = {
            "conversation_id": conversation_id,
            "workflow_id": self.workflow_id,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                headers=self._get_headers(),
                json=payload,
            )
            response.raise_for_status()
            return response.json()
