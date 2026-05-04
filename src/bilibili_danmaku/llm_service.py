import asyncio
import json
from pathlib import Path

import aiohttp

from .config import Config
from .logger import logger


class LLMService:
    """LLM 服务类"""

    def __init__(self, config: type[Config] = Config):
        self.config = config
        self.chat_history: list[dict[str, str]] = []
        self._lock = asyncio.Lock()
        # 从配置文件加载模型池子
        self.model_pool, self.default_model = self._load_model_pool()
        # 从配置文件加载角色提示
        self.character_prompt = self._load_character_prompt()
        # 初始化当前模型
        self.current_model = self.default_model
        self.current_model_name = self.model_pool.get(self.current_model, self.config.OPENROUTER_MODEL)
        # 模型池列表，用于自动切换
        self.model_pool_list = list(self.model_pool.keys())
        self.current_model_index = self.model_pool_list.index(self.current_model) if self.current_model in self.model_pool_list else 0

    def _load_character_prompt(self) -> str:
        """从配置文件加载角色提示"""
        config_path = Path(self.config.CHARACTER_CONFIG)
        default_prompt = """名字：心翎 （XinLing）,身高：166cm, 身份：言灵使"""
        
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    character_prompt = f.read().strip()
                    logger.info(f"从配置文件加载角色提示: {config_path}")
                    return character_prompt
            else:
                logger.warning(f"角色配置文件不存在: {config_path}，使用默认配置")
                return default_prompt
        except Exception as e:
            logger.error(f"加载角色配置失败: {e}，使用默认配置")
            return default_prompt

    def _load_model_pool(self) -> tuple[dict[str, str], str]:
        """从配置文件加载模型池子"""
        config_path = Path(self.config.MODEL_POOL_CONFIG)
        default_model_pool = {
            "minimax": "minimax/minimax-m2.5:free"
        }
        default_model = "minimax"
        
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    model_pool = config_data.get('model_pool', default_model_pool)
                    default_model = config_data.get('default_model', default_model)
                    logger.info(f"从配置文件加载模型池子: {config_path}")
                    return model_pool, default_model
            else:
                logger.warning(f"模型池子配置文件不存在: {config_path}，使用默认配置")
                return default_model_pool, default_model
        except Exception as e:
            logger.error(f"加载模型池子配置失败: {e}，使用默认配置")
            return default_model_pool, default_model

    async def call(self, user_message: str) -> str:
        """调用 LLM 获取回复"""
        async with self._lock:
            return await self._call_llm(user_message)

    async def _call_llm(self, user_message: str) -> str:
        """实际调用 LLM 的方法，支持自动切换模型"""
        # 尝试所有模型
        original_model = self.current_model
        attempted_models = set()
        
        while len(attempted_models) < len(self.model_pool_list):
            # 避免重复尝试同一个模型
            if self.current_model in attempted_models:
                self.switch_to_next_model()
                continue
            
            attempted_models.add(self.current_model)
            current_model_name = self.current_model_name
            
            logger.info(f"尝试使用模型: {self.current_model} ({current_model_name})")
            
            payload = {
                "model": current_model_name,
                "messages": [
                    {"role": "system", "content": self.character_prompt},
                    *self.chat_history,
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": self.config.MAX_TOKENS,
                "temperature": self.config.TEMPERATURE
            }

            headers = {
                "Authorization": f"Bearer {self.config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.config.OPENROUTER_API_URL,
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            reply = data["choices"][0]["message"]["content"].strip()

                            # 如果切换了模型，记录日志
                            if self.current_model != original_model:
                                logger.info(f"模型切换成功: {original_model} -> {self.current_model}")

                            # 更新历史记录
                            self._update_history(user_message, reply)

                            return reply
                        else:
                            logger.warning(f"LLM API 返回错误状态: {response.status} (模型: {self.current_model})")
                            # 切换到下一个模型
                            self.switch_to_next_model()
                            continue
            except asyncio.TimeoutError:
                logger.warning(f"LLM API 请求超时 (模型: {self.current_model})")
                # 切换到下一个模型
                self.switch_to_next_model()
                continue
            except Exception as e:
                logger.error(f"LLM API 调用失败: {e} (模型: {self.current_model})")
                # 切换到下一个模型
                self.switch_to_next_model()
                continue
        
        # 所有模型都尝试失败
        logger.error("所有模型都调用失败")
        return "抱歉，我现在有点忙，稍后再回答你哦！"

    def _update_history(self, user_message: str, assistant_reply: str) -> None:
        """更新聊天历史"""
        self.chat_history.append({"role": "user", "content": user_message})
        self.chat_history.append({"role": "assistant", "content": assistant_reply})

        # 限制历史长度
        if len(self.chat_history) > self.config.MAX_HISTORY:
            self.chat_history = self.chat_history[-self.config.MAX_HISTORY:]

    def clear_history(self) -> None:
        """清空历史记录"""
        self.chat_history.clear()

    def switch_model(self, model_key: str) -> bool:
        """切换模型"""
        if model_key in self.model_pool:
            self.current_model = model_key
            self.current_model_name = self.model_pool[model_key]
            # 切换模型时清空历史记录
            self.clear_history()
            return True
        return False

    def get_current_model(self) -> tuple[str, str]:
        """获取当前模型信息"""
        return self.current_model, self.current_model_name

    def get_available_models(self) -> list[str]:
        """获取可用模型列表"""
        return list(self.model_pool.keys())

    def get_next_model(self) -> str:
        """获取下一个模型"""
        self.current_model_index = (self.current_model_index + 1) % len(self.model_pool_list)
        return self.model_pool_list[self.current_model_index]

    def switch_to_next_model(self) -> tuple[str, str]:
        """切换到下一个模型"""
        next_model = self.get_next_model()
        self.switch_model(next_model)
        return self.current_model, self.current_model_name
