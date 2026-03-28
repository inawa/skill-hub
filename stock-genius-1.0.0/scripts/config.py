"""
Stock Genius - 集中配置文件
"""
import os

# 用户数据目录
BASE_DIR = os.path.expanduser("~/.stock_genius")
WATCHLIST_FILE = os.path.join(BASE_DIR, "watchlist.txt")

# 确保目录存在
os.makedirs(BASE_DIR, exist_ok=True)

# 通用 HTTP 请求头（模拟浏览器）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/json,text/plain,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# 新浪财经实时行情 API
SINA_API = "https://hq.sinajs.cn/list="
SINA_HEADERS = {
    **HEADERS,
    "Referer": "https://finance.sina.com.cn",
}

# 请求超时（秒）
TIMEOUT = 15
# 批量请求间隔（秒）
REQUEST_DELAY = 0.5


def get_market_prefix(code: str) -> str:
    """将6位股票代码转换为带市场前缀的代码（sh/sz/bj）。"""
    code = code.strip()
    if code.startswith(("sh", "sz", "bj")):
        return code
    if code.startswith("6"):
        return f"sh{code}"
    elif code.startswith(("0", "3")):
        return f"sz{code}"
    elif code.startswith(("8", "4")):
        return f"bj{code}"
    return f"sh{code}"


def load_watchlist() -> list:
    """加载自选股列表，返回 (代码, 名称) 元组列表。"""
    if not os.path.exists(WATCHLIST_FILE):
        return []
    results = []
    with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 1)
            if len(parts) == 2:
                results.append((parts[0], parts[1]))
            else:
                results.append((parts[0], ""))
    return results


def save_watchlist(stocks: list):
    """保存自选股列表。stocks: (代码, 名称) 元组列表。"""
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        for code, name in stocks:
            f.write(f"{code}|{name}\n")
