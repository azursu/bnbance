import requests
import os

# 测试推送：直接发微信消息
token = os.getenv("PUSHPLUS_TOKEN")

print("正在发送测试消息...")
data = {
    "token": token,
    "title": "✅ 测试成功！",
    "content": "你的币安行情监控配置正常！每天8点会自动扫描，出现信号会第一时间提醒你！"
}

requests.post("https://www.pushplus.plus/send", json=data)
print("测试消息已发送！请查看微信！")
