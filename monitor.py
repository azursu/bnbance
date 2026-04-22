import requests
import time
import os

# 币安合约API地址
BASE_URL = "https://fapi.binance.com"

def get_all_perpetual_symbols():
    """获取所有正在交易的永续合约列表"""
    resp = requests.get(f"{BASE_URL}/fapi/v1/exchangeInfo")
    data = resp.json()
    symbols = []
    for s in data['symbols']:
        # 筛选出永续合约、且正在交易的
        if s['contractType'] == 'PERPETUAL' and s['status'] == 'TRADING':
            symbols.append(s['symbol'])
    return symbols

def get_klines(symbol, interval='1d', limit=61):
    """获取单个合约的日K线数据，默认取最近61根（满足计算需求）"""
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit
    }
    resp = requests.get(f"{BASE_URL}/fapi/v1/klines", params=params)
    return resp.json()

def check_signal(klines):
    """检查是否满足你的信号条件"""
    # 上市时间不够61天的新币直接跳过（数据不够计算）
    if len(klines) < 61:
        return False
    
    # 提取收盘价和成交量
    closes = []
    volumes = []
    for k in klines:
        closes.append(float(k[4]))  # 收盘价
        volumes.append(float(k[5])) # 成交量
    
    # 最新的收盘价、成交量
    latest_close = closes[-1]
    latest_volume = volumes[-1]
    
    # 计算60日均线：最近60根收盘价的平均值
    ma60 = sum(closes[-60:]) / 60
    
    # 计算前20根成交量的平均值：最新K线之前的20根
    prev_20_vol = volumes[-21:-1]
    avg_prev_20_vol = sum(prev_20_vol) / 20
    
    # 判断两个条件：突破60日均线 + 成交量翻倍
    if latest_close > ma60 and latest_volume > avg_prev_20_vol * 2:
        return True
    return False

def send_wechat_notify(token, signal_symbols):
    """通过PushPlus给你发微信提醒"""
    if not signal_symbols:
        print("没有符合条件的合约，不发消息")
        return
    
    # 构造消息内容
    title = "币安行情信号提醒"
    content = "【币安永续合约信号提醒】\n"
    content += "以下合约满足你的条件：\n"
    for s in signal_symbols:
        content += f"- {s}\n"
    content += "\n触发条件：日K收盘突破60日均线，成交量大于前20日平均2倍"
    
    # 调用PushPlus接口发微信消息
    data = {
        "token": token,
        "title": title,
        "content": content
    }
    requests.post("https://www.pushplus.plus/send", json=data)
    print(f"已发送微信提醒，符合条件的合约：{signal_symbols}")

def main():
    # 读取你配置的Token
    token = os.getenv("PUSHPLUS_TOKEN")
    if not token:
        print("错误：未配置PUSHPLUS_TOKEN")
        return
    
    print("开始获取永续合约列表...")
    symbols = get_all_perpetual_symbols()
    print(f"共找到 {len(symbols)} 个交易中的永续合约")
    
    signals = []
    for symbol in symbols:
        try:
            print(f"正在处理 {symbol}...")
            klines = get_klines(symbol)
            if check_signal(klines):
                signals.append(symbol)
            # 加0.1秒延时，避免触发币安API限流
            time.sleep(0.1)
        except Exception as e:
            print(f"处理 {symbol} 出错：{e}")
            continue
    
    # 发送提醒
    send_wechat_notify(token, signals)

if __name__ == "__main__":
    main()
