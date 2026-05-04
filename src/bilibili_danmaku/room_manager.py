import asyncio
from typing import Optional

from bilibili_api import live

from .config import Config
from .event_handler import EventHandler
from .logger import logger
from .models import DanmakuEvent, GiftEvent


class LiveRoomManager:
    """直播间连接管理器"""

    def __init__(self, config: type[Config] = Config):
        self.config = config
        self._room: Optional[live.LiveDanmaku] = None
        self._connected = False
        self._reconnect_count = 0

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def connect(
        self,
        event_handler: EventHandler,
        on_connect: Optional[callable] = None,
        on_disconnect: Optional[callable] = None
    ) -> None:
        """连接到直播间"""
        self._room = live.LiveDanmaku(self.config.ROOM_ID)

        # 注册事件监听器
        self._room.add_event_listener("DANMU_MSG", self._create_danmaku_handler(event_handler))
        self._room.add_event_listener("SEND_GIFT", self._create_gift_handler(event_handler))

        while True:
            try:
                logger.info(f"正在连接直播间 {self.config.ROOM_ID}...")
                await self._room.connect()
                self._connected = True
                self._reconnect_count = 0

                if on_connect:
                    on_connect()

                logger.info("连接成功！开始接收弹幕...")

                # 保持连接
                while self._connected:
                    if not self._room._connected:
                        logger.warning("连接已断开")
                        self._connected = False
                        break
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"连接失败: {e}")
                self._connected = False
                self._reconnect_count += 1

                if self._reconnect_count >= self.config.MAX_RECONNECT_ATTEMPTS:
                    logger.error("达到最大重连次数，程序退出")
                    break

                delay = self.config.RECONNECT_DELAY
                logger.info(f"{delay} 秒后尝试重连...")
                await asyncio.sleep(delay)

                if on_disconnect:
                    on_disconnect()

    def _create_danmaku_handler(self, event_handler: EventHandler):
        """创建弹幕事件处理器"""
        async def handler(event):
            try:
                data = event["data"]
                user_name, message = self._parse_danmaku(data)

                if user_name and message:
                    danmaku_event = DanmakuEvent(
                        user_name=user_name,
                        message=message,
                        raw_data=data
                    )
                    await event_handler.handle_danmaku(danmaku_event)
            except Exception as e:
                logger.error(f"处理弹幕事件失败: {e}")

        return handler

    def _create_gift_handler(self, event_handler: EventHandler):
        """创建礼物事件处理器"""
        async def handler(event):
            try:
                data = event["data"]
                user_name = data.get("uname", "未知用户")
                gift_name = data.get("giftName", "礼物")
                num = data.get("num", 1)

                gift_event = GiftEvent(
                    user_name=user_name,
                    gift_name=gift_name,
                    num=num,
                    raw_data=data
                )
                await event_handler.handle_gift(gift_event)
            except Exception as e:
                logger.error(f"处理礼物事件失败: {e}")

        return handler

    def _parse_danmaku(self, data: dict) -> tuple[str, str]:
        """解析弹幕数据"""
        user_name = "未知用户"
        message = ""

        # 尝试格式1: uname + msg
        if "uname" in data and "msg" in data:
            user_name = data.get("uname", "未知用户")
            message = data.get("msg", "")

        # 尝试格式2: info 数组
        elif "info" in data and isinstance(data["info"], list):
            info = data["info"]
            if len(info) > 1:
                message = str(info[1])
            if len(info) > 2 and isinstance(info[2], list):
                if len(info[2]) > 1:
                    user_name = str(info[2][1])
                elif len(info[2]) > 0:
                    user_name = str(info[2][0])

        return user_name, message

    async def disconnect(self) -> None:
        """断开连接"""
        if self._room:
            try:
                await self._room.disconnect()
            except Exception as e:
                logger.error(f"断开连接失败: {e}")
        self._connected = False
