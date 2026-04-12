# 纯终端测试，无需 Telegram，无需打开 MongoDB
from ChatGPT_HKBU import ChatGPT
import configparser
import DBUtil  # 组员写的工具

# 读取配置
config = configparser.ConfigParser()
config.read('config.ini')

# 初始化AI
gpt = ChatGPT(config)

# 测试用户（不用Telegram）
user_id = "test_user_123"

# 测试消息
messages = [
    "I am very sad today",
    "I feel stressed about exam",
    "I am tired and unhappy"
]

print("=== 测试开始 ===")

# 发送消息并保存到数据库（自动带时间戳）
for msg in messages:
    reply = gpt.submit(msg)
    # 调用组员的真实函数！
    DBUtil.save_chat_history(config, user_id, msg, reply)
    print(f"✅ 已保存：{msg}")

# 读取数据，查看时间戳
print("\n=== 查看时间戳 ===")
chats = DBUtil.get_recent_chat_history(config, user_id)
for chat in chats:
    print("消息：", chat["user_message"])
    print("时间戳：", chat["timestamp"])
    print("-----------------")

# 生成情绪总结
print("\n=== AI 情绪总结 ===")
history_text = ""
for chat in chats:
    history_text += "User: " + chat["user_message"] + "\n"

prompt = f"""
Summarize this user's emotion in one sentence:
{history_text}
"""

summary = gpt.submit(prompt)
print("总结：", summary)

print("\n=== 测试全部完成 ===")
