import asyncio
import time

from .config import Config
from .danmaku_sender import DanmakuSender
from .logger import logger
from .models import GiftEvent


class GiftThanker:
    """礼物感谢器，带冷却机制防止刷屏"""

    def __init__(self, sender: DanmakuSender, config: type[Config] = Config):
        self.sender = sender
        self.config = config
        self._last_thank_time: float = 0  # 上次感谢时间
        self._user_last_thank: dict[str, float] = {}  # 每个用户上次感谢时间
        self._lock = asyncio.Lock()

    async def thank(self, event: GiftEvent) -> bool:
        """感谢礼物赠送者"""
        async with self._lock:
            current_time = time.time()

            # 全局冷却检查
            if current_time - self._last_thank_time < self.config.GIFT_THANK_COOLDOWN:
                logger.debug(f"礼物感谢冷却中，跳过: {event.user_name}")
                return False

            # 用户冷却检查
            last_time = self._user_last_thank.get(event.user_name, 0)
            if current_time - last_time < self.config.USER_THANK_COOLDOWN:
                logger.debug(f"用户 {event.user_name} 感谢冷却中，跳过")
                return False

            # 构造感谢消息
            message = f"感谢 {event.user_name} 赠送的 {event.num} 个 {event.gift_name}！"

            # 发送感谢
            success = await self.sender.send(message)

            if success:
                self._last_thank_time = current_time
                self._user_last_thank[event.user_name] = current_time
                logger.info(f"已感谢: {message}")

            return success

    def cleanup_old_users(self) -> None:
        """清理旧的用户记录"""
        current_time = time.time()
        expire_time = self.config.USER_THANK_COOLDOWN * 2
        self._user_last_thank = {
            user: t for user, t in self._user_last_thank.items()
            if current_time - t < expire_time
        }
