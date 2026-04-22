import requests
import os

# 打印日志，帮你找错误
print("=== 脚本开始运行 ===")
token = os.getenv("PUSHPLUS_TOKEN")
print(f"获取到的Token: {token}")

if not token:
    print("❌ 错误：没有配置 PUSHPLUS_TOKEN !!!")
    exit(1)

print("✅ Token 配置正常")

# 测试推送
try:
    data = {
        "token": token,
        "title": "测试通知",
        "content": "监控脚本运行成功！"
    }
    requests.post("https://www.pushplus.plus/send", json=data)
    print("✅ 微信推送测试成功")
except Exception as e:
    print(f"❌ 推送失败: {e}")
    exit(1)

print("=== 脚本运行完毕 ===")
