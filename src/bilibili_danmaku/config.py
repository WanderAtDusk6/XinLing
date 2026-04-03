import os


class Config:
    """配置类，从环境变量加载配置"""

    # 直播间配置
    ROOM_ID: int = int(os.getenv("BILIBILI_ROOM_ID", "1990578187"))

    # Bilibili Cookie 配置
    SESSDATA: str = os.getenv("BILIBILI_SESSDATA", "")
    BILI_JCT: str = os.getenv("BILIBILI_BILI_JCT", "")
    BUVID3: str = os.getenv("BILIBILI_BUVID3", "")

    # OpenRouter API 配置
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_API_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "minimax/minimax-m2.5:free")

    # 模型池子配置文件路径
    MODEL_POOL_CONFIG: str = os.getenv("MODEL_POOL_CONFIG", "./model_pool.json")
    # 角色配置文件路径
    CHARACTER_CONFIG: str = os.getenv("CHARACTER_CONFIG", "src/character_prompt.md")

    # LLM 配置
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "100"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))

    # 功能开关
    TEST_MODE: bool = os.getenv("TEST_MODE", "false").lower() == "true"
    TEST_DANMAKU_ONLY: bool = os.getenv("TEST_DANMAKU_ONLY", "false").lower() == "true"
    TEST_LLM_ONLY: bool = os.getenv("TEST_LLM_ONLY", "false").lower() == "true"

    # 行为配置
    TRIGGER_PREFIX: str = os.getenv("TRIGGER_PREFIX", "@xl")
    MAX_DANMAKU_LENGTH: int = int(os.getenv("MAX_DANMAKU_LENGTH", "40"))
    DANMAKU_PREFIX: str = os.getenv("DANMAKU_PREFIX", "[心翎]:")
    MAX_HISTORY: int = int(os.getenv("MAX_HISTORY", "10"))

    # 礼物感谢冷却（秒）
    GIFT_THANK_COOLDOWN: int = int(os.getenv("GIFT_THANK_COOLDOWN", "60"))
    # 同一用户感谢冷却（秒）
    USER_THANK_COOLDOWN: int = int(os.getenv("USER_THANK_COOLDOWN", "300"))

    # 重连配置
    RECONNECT_DELAY: int = int(os.getenv("RECONNECT_DELAY", "5"))
    MAX_RECONNECT_ATTEMPTS: int = int(os.getenv("MAX_RECONNECT_ATTEMPTS", "10"))

    @classmethod
    def validate(cls) -> list[str]:
        """验证必要配置，返回缺失的配置项列表"""
        missing = []
        if not cls.SESSDATA:
            missing.append("BILIBILI_SESSDATA")
        if not cls.BILI_JCT:
            missing.append("BILIBILI_BILI_JCT")
        if not cls.BUVID3:
            missing.append("BILIBILI_BUVID3")
        if not cls.OPENROUTER_API_KEY:
            missing.append("OPENROUTER_API_KEY")
        return missing
