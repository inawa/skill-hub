"""
Stock Genius - 搜索股票（支持代码精确查询和名称模糊搜索）
用法: python3 query_stock.py <代码或名称>
"""
import sys
import re
import json
import requests
from config import HEADERS, TIMEOUT


def query_by_code(code: str):
    """通过6位代码精确查询股票信息。"""
    try:
        url = f"https://stockpage.10jqka.com.cn/{code}/"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.encoding = "utf-8"
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.find("title")
        if title:
            name = title.text.split("(")[0].strip()
            print(f"[找到] {code} - {name}")
            print(f"  详情: https://stockpage.10jqka.com.cn/{code}/")
            return True
    except Exception as e:
        print(f"[错误] 查询 {code} 失败: {e}")
    return False


def query_by_name(keyword: str):
    """通过名称关键词模糊搜索股票。"""
    try:
        url = f"https://news.10jqka.com.cn/public/index_keyboard_{keyword}_0_20_jsonp.html"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.encoding = "utf-8"
        text = resp.text.strip()

        # 解析 JSONP 响应: jsonp(["1||600519 贵州茅台 股票", ...])
        match = re.search(r'\((\[.*?\])\)', text, re.DOTALL)
        if not match:
            print(f"[提示] 未找到与「{keyword}」相关的结果")
            return

        data = json.loads(match.group(1))
        results = []
        for item in data:
            if isinstance(item, str):
                # 格式: "market||code name type"
                parts = item.split("||")
                if len(parts) == 2:
                    market = parts[0].strip()
                    rest = parts[1].strip().split()
                    if len(rest) >= 2 and market == "1":
                        code = rest[0]
                        name = rest[1]
                        if len(code) == 6 and code.isdigit():
                            results.append({"code": code, "name": name})
            elif isinstance(item, dict):
                if item.get("market") == "1" and len(item.get("code", "")) == 6:
                    results.append({
                        "code": item["code"],
                        "name": item.get("short", item.get("name", "")),
                    })

        if not results:
            print(f"[提示] 未找到与「{keyword}」相关的A股股票")
            return

        print(f"=== 搜索结果：「{keyword}」（共 {len(results)} 条）===")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r['code']} - {r['name']}")
        print("=" * 40)

    except Exception as e:
        print(f"[错误] 搜索失败: {e}")


def main():
    if len(sys.argv) < 2:
        print("用法: python3 query_stock.py <股票代码或名称>")
        sys.exit(1)

    query = sys.argv[1].strip()

    if query.isdigit() and len(query) == 6:
        query_by_code(query)
    else:
        query_by_name(query)


if __name__ == "__main__":
    main()
