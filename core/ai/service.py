"""
Coze AI 智能体 Service 层
处理业务逻辑和错误处理
"""
from typing import Optional, Dict, Any, AsyncGenerator, List
from core.ai.client import CozeClient
import json
import logging
import asyncio

logger = logging.getLogger(__name__)


class CozeService:
    """
    Coze 智能体服务层
    处理与智能体相关的业务逻辑
    """

    def __init__(self):
        """初始化 Coze 服务"""
        self.client = CozeClient()

    async def initiate_conversation(
        self,
        user_id: str,
        user_input: str,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        发起对话

        Args:
            user_id: 用户 ID
            user_input: 用户输入内容
            conversation_id: 对话 ID（可选）

        Returns:
            包含 id(chat_id)、conversation_id 和 status 的响应
        """
        try:
            logger.info(
                f"发起对话: user_id={user_id}, input_length={len(user_input)}"
            )
            response = await self.client.start_chat(
                user_id=user_id,
                user_input=user_input,
                conversation_id=conversation_id,
            )
            logger.info(f"对话发起成功: {response}")
            return response
        except Exception as e:
            logger.error(f"发起对话失败: {str(e)}")
            raise

    async def initiate_conversation_stream(
        self,
        user_id: str,
        user_input: str,
        conversation_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        发起流式对话

        Args:
            user_id: 用户 ID
            user_input: 用户输入内容
            conversation_id: 对话 ID（可选）

        Yields:
            流式响应内容
        """
        try:
            logger.info(
                f"发起流式对话: user_id={user_id}, input_length={len(user_input)}"
            )
            async for chunk in self.client.start_chat_stream(
                user_id=user_id,
                user_input=user_input,
                conversation_id=conversation_id,
            ):
                yield chunk
        except Exception as e:
            logger.error(f"流式对话发生错误: {str(e)}")
            raise

    async def get_conversation_details(
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
        try:
            logger.info(
                f"获取对话详情: conversation_id={conversation_id}, chat_id={chat_id}"
            )
            response = await self.client.retrieve_chat(
                conversation_id=conversation_id,
                chat_id=chat_id,
            )
            logger.info(f"对话详情获取成功")
            return response
        except Exception as e:
            logger.error(f"获取对话详情失败: {str(e)}")
            raise

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
        try:
            logger.info(
                f"获取对话消息: conversation_id={conversation_id}, chat_id={chat_id}"
            )
            messages = await self.client.get_chat_messages(
                conversation_id=conversation_id,
                chat_id=chat_id,
            )
            logger.info(f"对话消息获取成功: {len(messages)} 条消息")
            return messages
        except Exception as e:
            logger.error(f"获取对话消息失败: {str(e)}")
            raise

    async def cancel_conversation(
        self,
        conversation_id: str,
    ) -> Dict[str, Any]:
        """
        取消对话

        Args:
            conversation_id: 对话 ID

        Returns:
            取消操作的响应
        """
        try:
            logger.info(f"取消对话: conversation_id={conversation_id}")
            response = await self.client.cancel_chat(
                conversation_id=conversation_id,
            )
            logger.info(f"对话取消成功")
            return response
        except Exception as e:
            logger.error(f"取消对话失败: {str(e)}")
            raise

    async def call_ai_bot(
        self,
        user_id: str,
        user_input: str,
        max_retries: int = 30,
        retry_interval: float = 1.0,
    ) -> Dict[str, Any]:
        """
        调用 AI 智能体进行非流式问答
        完整流程：发起对话 -> 等待完成 -> 获取消息列表

        Args:
            user_id: 用户 ID
            user_input: 用户的问题输入
            max_retries: 最大重试次数（等待 AI 完成的次数）
            retry_interval: 重试间隔（秒）

        Returns:
            包含对话信息和智能体回答的响应
        """
        try:
            logger.info(f"调用 AI 智能体: user_id={user_id}")

            # 第一步：发起对话
            chat_response = await self.initiate_conversation(
                user_id=user_id,
                user_input=user_input,
            )

            chat_id = chat_response.get('id')
            conversation_id = chat_response.get('conversation_id')
            status = chat_response.get('status')

            logger.info(f"对话已发起: chat_id={chat_id}, status={status}")

            # 第二步：等待 AI 完成处理（轮询检查状态）
            retry_count = 0
            while status != 'completed' and retry_count < max_retries:
                await asyncio.sleep(retry_interval)
                chat_details = await self.get_conversation_details(
                    conversation_id=conversation_id,
                    chat_id=chat_id,
                )
                status = chat_details.get('status')
                retry_count += 1
                logger.info(f"检查对话状态 (重试 {retry_count}/{max_retries}): status={status}")

            if status != 'completed':
                logger.warning(f"AI 处理超时，状态仍为: {status}")

            logger.info(f"对话详情: {chat_details}")

            # 第三步：获取对话消息列表
            messages = await self.get_chat_messages(
                conversation_id=conversation_id,
                chat_id=chat_id,
            )

            logger.info(f"获取到 {len(messages)} 条消息")

            # 提取最后一个完整的助手回答（role 为 assistant 且 type 为 answer）
            # 遍历消息，找到最后一个完整答案
            ai_response = None
            for msg in reversed(messages):
                if msg.get('role') == 'assistant' and msg.get('type') == 'answer':
                    content = msg.get('content', '').strip()
                    # 过滤掉"正在为你搜索"这样的过渡消息（长度过短或仅为占位符）
                    if content and len(content) > 8 and not content.startswith('{'):
                        ai_response = content
                        break

            # 如果没找到完整答案，取最后一个 answer 类型的消息
            if not ai_response:
                for msg in reversed(messages):
                    if msg.get('role') == 'assistant' and msg.get('type') == 'answer':
                        ai_response = msg.get('content')
                        break

            # 构建返回结果
            result = {
                'conversation_id': conversation_id,
                'chat_id': chat_id,
                'user_input': user_input,
                'ai_response': ai_response,
                'status': status,
                'messages': messages,
                'usage': chat_details.get('usage'),
            }

            logger.info(f"AI 调用完成")
            return result

        except Exception as e:
            logger.error(f"调用 AI 智能体失败: {str(e)}")
            raise


# 创建全局单例实例
coze_service = CozeService()
