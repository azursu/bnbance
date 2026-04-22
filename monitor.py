import requests
import time
import os

BASE_URL = "https://fapi.binance.com"

def get_all_perpetual_symbols():
    try:
        resp = requests.get(f"{BASE_URL}/fapi/v1/exchangeInfo", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        symbols = []
        for s in data['symbols']:
            if s['contractType'] == 'PERPETUAL' and s['status'] == 'TRADING':
                symbols.append(s['symbol'])
        return symbols
    except:
        return []

def get_klines(symbol, interval='1d', limit=61):
    try:
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        resp = requests.get(f"{BASE_URL}/fapi/v1/klines", params=params, timeout=10)
        return resp.json()
    except:
        return []

def check_signal(klines):
    if len(klines) < 61:
        return False

    closes = []
    volumes = []
    for k in klines:
        closes.append(float(k[4]))
        volumes.append(float(k[5]))

    latest_close = closes[-1]
    latest_volume = volumes[-1]
    ma60 = sum(closes[-60:]) / 60
    prev_20 = volumes[-21:-1]
    avg_20 = sum(prev_20) / 20

    return latest_close > ma60 and latest_volume > avg_20 * 2

def send_pushplus(token, symbols):
    if not symbols:
        print("无信号")
        return

    content = "【币安永续合约信号提醒】\n"
    content += "满足条件：收盘突破60日均线 + 成交量大于前20日均量2倍\n\n"
    for s in symbols:
        content += f"✅ {s}\n"

    data = {
        "token": token,
        "title": "币安行情信号提醒",
        "content": content
    }
    try:
        requests.post("https://www.pushplus.plus/send", json=data, timeout=10)
        print("推送成功")
    except:
        print("推送失败")

def main():
    token = os.getenv("PUSHPLUS_TOKEN", "")
    if not token:
        print("ERROR：未配置 PUSHPLUS_TOKEN")
        return

    symbols = get_all_perpetual_symbols()
    print(f"获取到 {len(symbols)} 个合约")

    signals = []
    for s in symbols:
        try:
            klines = get_klines(s)
            if check_signal(klines):
                signals.append(s)
            time.sleep(0.1)
        except:
            continue

    send_pushplus(token, signals)
    print("执行完成")

if __name__ == "__main__":
    main()
