from typing import Optional

from bilibili_api import live, Credential
from bilibili_api.utils.danmaku import Danmaku

from .config import Config
from .logger import logger


class DanmakuSender:
    """弹幕发送器"""

    def __init__(self, config: type[Config] = Config):
        self.config = config
        self._credential: Optional[Credential] = None
        self._room: Optional[live.LiveRoom] = None

    def _get_credential(self) -> Credential:
        """获取认证凭据"""
        if self._credential is None:
            self._credential = Credential(
                sessdata=self.config.SESSDATA,
                bili_jct=self.config.BILI_JCT,
                buvid3=self.config.BUVID3
            )
        return self._credential

    def _get_room(self) -> live.LiveRoom:
        """获取直播间对象"""
        if self._room is None:
            self._room = live.LiveRoom(self.config.ROOM_ID, credential=self._get_credential())
        return self._room

    async def send(self, message: str) -> bool:
        """发送弹幕"""
        if not message:
            return False

        try:
            # 截断消息长度
            truncated_message = self._truncate_message(message)
            # 添加前缀
            full_message = f"{self.config.DANMAKU_PREFIX}{truncated_message}"

            logger.info(f"发送弹幕: {full_message}")

            danmaku = Danmaku(full_message)
            room = self._get_room()
            await room.send_danmaku(danmaku)

            logger.debug(f"弹幕发送成功")
            return True

        except Exception as e:
            logger.error(f"发送弹幕失败: {e}")
            return False

    def _truncate_message(self, message: str) -> str:
        """截断消息长度"""
        max_length = self.config.MAX_DANMAKU_LENGTH
        prefix = self.config.DANMAKU_PREFIX
        available_length = max_length - len(prefix) - 3  # 预留 "..." 的位置

        if len(message) > available_length:
            return message[:available_length] + "..."
        return message
