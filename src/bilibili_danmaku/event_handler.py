import asyncio
from .config import Config
from .danmaku_sender import DanmakuSender
from .gift_thanker import GiftThanker
from .llm_service import LLMService
from .logger import logger
from .models import DanmakuEvent, GiftEvent


class EventHandler:
    """事件处理器"""

    def __init__(
        self,
        llm_service: LLMService,
        sender: DanmakuSender,
        thankier: GiftThanker,
        config: type[Config] = Config
    ):
        self.llm_service = llm_service
        self.sender = sender
        self.thanker = thankier
        self.config = config

    async def handle_danmaku(self, event: DanmakuEvent) -> None:
        """处理弹幕事件"""
        logger.info(f"[弹幕] {event.user_name}: {event.message}")

        # 跳过空消息
        if not event.message:
            return

        # 测试模式
        if self.config.TEST_MODE and self.config.TEST_DANMAKU_ONLY:
            return

        # 检查触发前缀
        if not event.message.startswith(self.config.TRIGGER_PREFIX):
            logger.debug("非触发前缀，跳过回复")
            return

        # 提取实际消息内容（去掉前缀）
        actual_message = event.message[len(self.config.TRIGGER_PREFIX):].strip()
        if not actual_message:
            return

        # 处理模型切换命令
        if actual_message.startswith("切换模型"):
            await self._handle_model_switch(event, actual_message)
            return
        
        # 处理模型列表命令
        if actual_message.startswith("模型列表"):
            await self._handle_model_list(event)
            return
            
        # 处理当前模型命令
        if actual_message.startswith("当前模型"):
            await self._handle_current_model(event)
            return

        # 构建 prompt，添加长度限制说明
        prompt = f"{event.user_name}说: {event.message}\n\n（请回复少于40词，保持简洁。）"

        # 调用 LLM
        try:
            reply = await self.llm_service.call(prompt)
            logger.info(f"[回复] {event.user_name}: {reply}")

            # 处理分段输出
            if len(reply) <= 80:
                # 少于或等于80词，尝试分两段输出
                # 简单的分段逻辑：按句号或逗号分割
                import re
                sentences = re.split('[。，]', reply)
                sentences = [s.strip() for s in sentences if s.strip()]
                
                if len(sentences) >= 2:
                    # 分成两段输出
                    first_part = '。'.join(sentences[:len(sentences)//2]) + '。'
                    second_part = '。'.join(sentences[len(sentences)//2:]) + '。'
                    
                    if first_part and second_part:
                        await self.sender.send(first_part)
                        await asyncio.sleep(0.5)  # 短暂延迟，避免发送过快
                        await self.sender.send(second_part)
                        return
            
            # 正常输出
            await self.sender.send(reply)

        except Exception as e:
            logger.error(f"处理弹幕失败: {e}")

    async def _handle_model_switch(self, event: DanmakuEvent, message: str) -> None:
        """处理模型切换命令"""
        # 提取模型名称
        model_parts = message.split(" ")
        if len(model_parts) < 2:
            await self.sender.send("请指定要切换的模型名称，例如: @xl 切换模型 minimax")
            return
        
        model_key = model_parts[1].strip()
        success = self.llm_service.switch_model(model_key)
        
        if success:
            current_model, model_name = self.llm_service.get_current_model()
            await self.sender.send(f"已成功切换到模型: {current_model} ({model_name})")
            logger.info(f"模型已切换到: {current_model} ({model_name})")
        else:
            available_models = ", ".join(self.llm_service.get_available_models())
            await self.sender.send(f"无效的模型名称，请从以下模型中选择: {available_models}")

    async def _handle_model_list(self, event: DanmakuEvent) -> None:
        """处理模型列表命令"""
        available_models = self.llm_service.get_available_models()
        models_str = ", ".join(available_models)
        await self.sender.send(f"可用模型列表: {models_str}")

    async def _handle_current_model(self, event: DanmakuEvent) -> None:
        """处理当前模型命令"""
        current_model, model_name = self.llm_service.get_current_model()
        await self.sender.send(f"当前使用的模型: {current_model} ({model_name})")

    async def handle_gift(self, event: GiftEvent) -> None:
        """处理礼物事件"""
        logger.info(f"[礼物] {event.user_name} 赠送了 {event.num} 个 {event.gift_name}")

        # 测试模式
        if self.config.TEST_MODE:
            return

        # 感谢礼物
        await self.thanker.thank(event)
