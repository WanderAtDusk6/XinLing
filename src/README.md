# B站直播间弹幕机器人

这是一个用于读取和回复B站直播间弹幕的Python脚本。

## 功能特性

- 实时接收并显示直播间弹幕
- 自动回复特定关键词的弹幕
- 处理礼物事件并发送感谢信息
- 测试模式，方便调试和测试
- 优雅退出机制

## 环境要求

- Python 3.7+
- bilibili-api 库

## 安装依赖

```bash
pip install bilibili-api-python
```

## 配置

在 `bilibili_danmaku.py` 文件中，你可以修改以下配置：

- `ROOM_ID`: 你的直播间ID（默认：1990578187）
- `TEST_MODE`: 总测试开关（默认：True）
- `TEST_DANMAKU_ONLY`: 仅测试弹幕读取（默认：False）
- `TEST_LLM_ONLY`: 仅测试LLM功能（默认：False）
- `OPENROUTER_API_KEY`: 你的OpenRouter API密钥
- `CHARACTER_PROMPT`: 虚拟主播的人设prompt

## 运行

### 1. 运行完整的弹幕机器人

```bash
python bilibili_danmaku.py
```

### 2. 单独测试LLM功能

修改配置：
```python
TEST_LLM_ONLY = True
```

然后运行：
```bash
python bilibili_danmaku.py
```

### 3. 仅测试弹幕读取（不回复）

修改配置：
```python
TEST_DANMAKU_ONLY = True
```

然后运行：
```bash
python bilibili_danmaku.py
```

## 测试指令

在直播间发送以下弹幕可以触发自动回复：

- `@xl 你好`：发送欢迎消息
- `@xl 测试`：发送测试成功消息
- `@xl 时间`：发送当前时间

注意：只有以 `@xl` 开头的弹幕才会触发LLM回复

## 注意事项

1. 确保你的直播间处于开播状态
2. 脚本需要保持运行才能持续接收和回复弹幕
3. 发送弹幕可能会受到B站的频率限制
4. 测试模式下，机器人会自动回复特定关键词

## 扩展

你可以根据需要修改 `on_danmaku` 函数，添加更多的回复逻辑和功能。
