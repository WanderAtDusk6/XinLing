from bilibili_api import sync

from .config import Config
from .danmaku_sender import DanmakuSender
from .event_handler import EventHandler
from .gift_thanker import GiftThanker
from .llm_service import LLMService
from .logger import logger
from .room_manager import LiveRoomManager


class BilibiliDanmakuBot:
    """Bilibili 弹幕机器人主类"""

    def __init__(self, config: type[Config] = Config):
        self.config = config

        # 初始化各组件
        self.llm_service = LLMService(config)
        self.sender = DanmakuSender(config)
        self.thanker = GiftThanker(self.sender, config)
        self.event_handler = EventHandler(self.llm_service, self.sender, self.thanker, config)
        self.room_manager = LiveRoomManager(config)

    async def run(self) -> None:
        """运行机器人"""
        # 验证配置
        missing_config = self.config.validate()
        if missing_config:
            logger.error(f"缺少必要配置: {', '.join(missing_config)}")
            logger.error("请设置环境变量或在代码中配置")
            return

        logger.info(f"=== B站直播间弹幕机器人 ===")
        logger.info(f"直播间ID: {self.config.ROOM_ID}")
        logger.info(f"测试模式: {'开启' if self.config.TEST_MODE else '关闭'}")
        logger.info(f"触发前缀: {self.config.TRIGGER_PREFIX}")

        try:
            await self.room_manager.connect(
                self.event_handler,
                on_connect=lambda: logger.info("已连接到直播间"),
                on_disconnect=lambda: logger.warning("连接已断开，准备重连")
            )
        except KeyboardInterrupt:
            logger.info("收到退出信号，正在关闭...")
        finally:
            await self.room_manager.disconnect()
            logger.info("程序已退出")

    async def test_llm(self) -> None:
        """测试 LLM 功能"""
        logger.info("=== LLM 测试模式 ===")
        logger.info("输入消息进行测试，输入 '退出' 结束测试")

        while True:
            try:
                user_input = input("你: ").strip()
                if user_input == "退出":
                    break
                if not user_input:
                    continue

                logger.info("正在生成回复...")
                reply = await self.llm_service.call(f"用户说: {user_input}")
                logger.info(f"[心翎]: {reply}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"测试出错: {e}")


def main():
    """主入口"""
    # 根据配置选择运行模式
    if Config.TEST_LLM_ONLY:
        # 仅测试 LLM
        bot = BilibiliDanmakuBot()
        sync(bot.test_llm())
    else:
        # 运行机器人
        bot = BilibiliDanmakuBot()
        sync(bot.run())
