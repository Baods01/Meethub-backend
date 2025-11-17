"""
Coze AI 智能体 Service 层
处理业务逻辑和错误处理
"""
from typing import Optional, Dict, Any, AsyncGenerator
from core.ai.client import CozeClient
import json
import logging

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
        conversation_name: str = "Default",
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        发起对话

        Args:
            user_id: 用户 ID
            user_input: 用户输入内容
            conversation_name: 对话名称
            stream: 是否使用流式响应

        Returns:
            包含 conversation_id 和 chat_id 的响应
        """
        try:
            logger.info(
                f"发起对话: user_id={user_id}, input_length={len(user_input)}"
            )
            response = await self.client.start_chat(
                user_id=user_id,
                user_input=user_input,
                conversation_name=conversation_name,
                stream=stream,
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
        conversation_name: str = "Default",
    ) -> AsyncGenerator[str, None]:
        """
        发起流式对话

        Args:
            user_id: 用户 ID
            user_input: 用户输入内容
            conversation_name: 对话名称

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
                conversation_name=conversation_name,
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

    async def process_user_input_for_recommendations(
        self,
        user_id: str,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        处理用户输入以获取推荐
        这是一个高级方法，结合了业务逻辑

        Args:
            user_id: 用户 ID
            user_input: 用户输入内容
            context: 额外的上下文信息

        Returns:
            智能体的推荐结果
        """
        try:
            logger.info(f"处理推荐请求: user_id={user_id}")

            # 构建自定义参数
            parameters = {
                "BOT_USER_INPUT": user_input,
                "CONVERSATION_NAME": "Recommendation",
            }

            # 如果有额外的上下文，添加到参数中
            if context:
                parameters.update(context)

            # 发起对话
            response = await self.client.start_chat(
                user_id=user_id,
                user_input=user_input,
                conversation_name="Recommendation",
                stream=False,
                parameters=parameters,
            )

            logger.info(f"推荐请求处理完成")
            return response
        except Exception as e:
            logger.error(f"处理推荐请求失败: {str(e)}")
            raise


# 创建全局单例实例
coze_service = CozeService()
