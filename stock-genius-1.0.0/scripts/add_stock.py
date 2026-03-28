"""
Stock Genius - 添加股票到自选股
用法: python3 add_stock.py <股票代码> [股票名称]
"""
import sys
import requests
from bs4 import BeautifulSoup
from config import HEADERS, TIMEOUT, load_watchlist, save_watchlist


def fetch_stock_name(code: str) -> str:
    """通过同花顺获取股票名称。"""
    try:
        url = f"https://stockpage.10jqka.com.cn/{code}/"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.find("title")
        if title:
            name = title.text.split("(")[0].strip()
            if name and name != code:
                return name
    except Exception:
        pass
    return ""


def main():
    if len(sys.argv) < 2:
        print("用法: python3 add_stock.py <股票代码> [股票名称]")
        sys.exit(1)

    code = sys.argv[1].strip()
    if not code.isdigit() or len(code) != 6:
        print(f"[错误] 无效的股票代码: {code}（必须为6位数字）")
        sys.exit(1)

    # 检查是否已在自选股中
    watchlist = load_watchlist()
    for c, n in watchlist:
        if c == code:
            print(f"[提示] {code}（{n}）已在自选股中")
            return

    # 获取股票名称
    if len(sys.argv) >= 3:
        name = sys.argv[2].strip()
    else:
        print(f"[信息] 正在获取 {code} 的股票名称...")
        name = fetch_stock_name(code)
        if not name:
            name = code
            print(f"[警告] 无法获取股票名称，将使用代码作为名称")

    watchlist.append((code, name))
    save_watchlist(watchlist)
    print(f"[成功] 已添加 {code}（{name}）到自选股")
    print(f"[信息] 自选股中共有 {len(watchlist)} 只股票")


if __name__ == "__main__":
    main()
