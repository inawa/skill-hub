"""
Stock Genius - 实时行情查询
用法: python3 realtime_quote.py <代码1> [代码2] [代码3] ...
"""
import sys
import requests
from config import SINA_API, SINA_HEADERS, TIMEOUT, get_market_prefix


def fetch_realtime(codes: list) -> list:
    """从新浪财经 API 获取实时行情。codes: 6位代码列表。"""
    prefixed = [get_market_prefix(c) for c in codes]
    url = SINA_API + ",".join(prefixed)
    try:
        resp = requests.get(url, headers=SINA_HEADERS, timeout=TIMEOUT)
        resp.encoding = "gbk"
    except Exception as e:
        print(f"[错误] 网络请求失败: {e}")
        return []

    results = []
    for line in resp.text.strip().split("\n"):
        line = line.strip()
        if not line or '="' not in line:
            continue
        try:
            var_part, data_part = line.split("=", 1)
            full_code = var_part.split("_")[-1]
            raw_code = full_code[2:]
            data = data_part.strip('";\n').split(",")
            if len(data) < 32:
                continue

            name = data[0]
            open_price = float(data[1]) if data[1] else 0
            yesterday_close = float(data[2]) if data[2] else 0
            current = float(data[3]) if data[3] else 0
            high = float(data[4]) if data[4] else 0
            low = float(data[5]) if data[5] else 0
            volume = int(float(data[8])) if data[8] else 0
            amount = float(data[9]) if data[9] else 0

            change = current - yesterday_close if yesterday_close else 0
            change_pct = (change / yesterday_close * 100) if yesterday_close else 0
            turnover_hand = volume // 100

            results.append({
                "code": raw_code,
                "name": name,
                "current": current,
                "change": change,
                "change_pct": change_pct,
                "open": open_price,
                "high": high,
                "low": low,
                "yesterday_close": yesterday_close,
                "volume": turnover_hand,
                "amount": amount,
            })
        except (ValueError, IndexError):
            continue

    return results


def format_quote(q: dict) -> str:
    """格式化单只股票行情。"""
    sign = "+" if q["change"] >= 0 else ""
    lines = [
        f"  股票: {q['code']} {q['name']}",
        f"  最新价: {q['current']:.2f}",
        f"  涨跌: {sign}{q['change']:.2f}（{sign}{q['change_pct']:.2f}%）",
        f"  开盘: {q['open']:.2f}  |  最高: {q['high']:.2f}  |  最低: {q['low']:.2f}",
        f"  昨收: {q['yesterday_close']:.2f}",
        f"  成交量: {q['volume']} 手  |  成交额: {q['amount']/10000:.2f} 万元",
    ]
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 realtime_quote.py <代码1> [代码2] ...")
        sys.exit(1)

    codes = [c.strip() for c in sys.argv[1:] if c.strip()]
    results = fetch_realtime(codes)

    if not results:
        print("[提示] 未返回数据，可能已收盘或代码无效")
        return

    print(f"=== 实时行情（共 {len(results)} 只）===")
    for q in results:
        print(f"\n{format_quote(q)}")
    print("\n" + "=" * 45)


if __name__ == "__main__":
    main()
