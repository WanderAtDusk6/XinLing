import time
from dataclasses import dataclass, field
from enum import Enum


class EventType(Enum):
    """事件类型"""
    DANMU_MSG = "DANMU_MSG"
    SEND_GIFT = "SEND_GIFT"
    INTERACT_WORD = "INTERACT_WORD"
    ROOM_RANK = "ROOM_RANK"


@dataclass
class DanmakuEvent:
    """弹幕事件"""
    user_name: str
    message: str
    raw_data: dict
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))


@dataclass
class GiftEvent:
    """礼物事件"""
    user_name: str
    gift_name: str
    num: int
    raw_data: dict
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
