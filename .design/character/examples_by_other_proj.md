# example

## OpenClaw

<https://github.com/openclaw/openclaw>

https://deepwiki.com/search/_10344717-4bd1-46b4-a05f-2974ae2c099c?mode=fast

code: <docs/zh-CN/concepts/agent-workspace.md>

## SillyTavern

### 角色部分

看上去角色设计部分，它比较简单，
主要是： 描述 + 个性摘要 + 对话示例

```
1. 基本信息
角色名称 (character_name): 角色的显示名称 index.html:5909-5911
头像 (avatar): 角色的头像图片 index.html:5916-5919
收藏标记 (fav): 是否收藏该角色 index.html:5925-5927
2. 核心描述字段
角色描述 (description): 角色的身体和精神特征描述 index.html:6429-6435
个性摘要 (personality): 角色性格的简要描述 index.html:6430-6435
场景 (scenario): 交互的背景和情境 index.html:6440-6448
第一条消息 (first_mes): 角色开始每次聊天的第一条消息 zh-cn.json:1101-1105
3. 高级定义
角色备注 (depth_prompt): 在指定深度和角色插入的文本 index.html:6453-6483
对话示例 (mes_example): 用于设定角色写作风格的示例对话 index.html:6498-6516
发言频率 (talkativeness): 角色在群聊中的发言频率 index.html:6485-6495
```

### 世界书部分

World Info(也称为 Lorebooks 或 Memory Books)
