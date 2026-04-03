from bilibili_api import sync
from bilibili_danmaku.bot import BilibiliDanmakuBot, Config

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
if __name__ == "__main__":
    main()

# @xl 断点测试，当前模型是什么