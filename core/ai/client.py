"""
Coze AI 智能体 HTTP 客户端
用于与 Coze API 进行通信
"""
import httpx
import json
from typing import Optional, Dict, Any, AsyncGenerator, List
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
        conversation_id: Optional[str] = None,
        auto_save_history: bool = True,
    ) -> Dict[str, Any]:
        """
        发起对话请求

        Args:
            user_id: 用户 ID
            user_input: 用户输入内容
            conversation_id: 对话 ID（可选，为空则创建新对话）
            auto_save_history: 是否自动保存历史记录

        Returns:
            API 响应字典，包含 id(chat_id)、conversation_id 和 status
        """
        url = f"{self.api_base_url}/chat"
        
        # 如果提供了 conversation_id，添加到 URL 参数中
        params = {}
        if conversation_id:
            params['conversation_id'] = conversation_id

        # 构建请求体
        payload = {
            "bot_id": self.bot_id,
            "user_id": user_id,
            "stream": False,
            "auto_save_history": auto_save_history,
            "additional_messages": [
                {
                    "role": "user",
                    "content": user_input,
                    "content_type": "text",
                }
            ]
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                headers=self._get_headers(),
                json=payload,
                params=params if params else None,
            )
            response.raise_for_status()
            result = response.json()
            # 返回 data 字段内容
            return result.get('data', {})

    async def start_chat_stream(
        self,
        user_id: str,
        user_input: str,
        conversation_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        发起流式对话请求

        Args:
            user_id: 用户 ID
            user_input: 用户输入内容
            conversation_id: 对话 ID（可选，为空则创建新对话）

        Yields:
            逐行的响应内容
        """
        url = f"{self.api_base_url}/chat"
        
        # 如果提供了 conversation_id，添加到 URL 参数中
        params = {}
        if conversation_id:
            params['conversation_id'] = conversation_id

        # 构建请求体
        payload = {
            "bot_id": self.bot_id,
            "user_id": user_id,
            "stream": True,
            "auto_save_history": True,
            "additional_messages": [
                {
                    "role": "user",
                    "content": user_input,
                    "content_type": "text",
                }
            ]
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                url,
                headers=self._get_headers(),
                json=payload,
                params=params if params else None,
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

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                url,
                headers=self._get_headers(),
                params=params,
            )
            response.raise_for_status()
            result = response.json()
            # 返回 data 字段内容
            return result.get('data', {})

    async def get_chat_messages(
        self,
        conversation_id: str,
        chat_id: str,
    ) -> List[Dict[str, Any]]:
        """
        获取对话消息列表

        Args:
            conversation_id: 对话 ID
            chat_id: 聊天消息 ID

        Returns:
            消息列表
        """
        url = f"{self.api_base_url}/chat/message/list"

        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                url,
                headers=self._get_headers(),
                params=params,
            )
            response.raise_for_status()
            result = response.json()
            # 返回 data 字段内容（消息列表）
            return result.get('data', [])

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
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                headers=self._get_headers(),
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            # 返回 data 字段内容
            return result.get('data', {})
