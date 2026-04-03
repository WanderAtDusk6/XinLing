import logging
import sys


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """配置日志系统"""
    logger = logging.getLogger("bilibili_danmaku")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # 格式化
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger


logger = setup_logging()
