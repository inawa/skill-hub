"""
Stock Genius - 新闻公告聚合
用法: python3 news.py <股票代码> [数量]
  数量: 获取条数（默认: 10）

从多个来源聚合个股最新新闻和公司公告。
"""
import sys
import re
import json
import requests
from bs4 import BeautifulSoup
from config import HEADERS, TIMEOUT


def fetch_news_10jqka(code: str, count: int = 10) -> list:
    """从同花顺获取个股新闻。"""
    news_list = []
    try:
        url = f"https://stockpage.10jqka.com.cn/{code}/news/"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        items = soup.select("ul.news-list li, .news_item, .list_item, .news-hd")
        for item in items[:count * 2]:
            a_tag = item.find("a")
            if a_tag and a_tag.get("href") and a_tag.text.strip():
                title = a_tag.text.strip()
                link = a_tag["href"]
                if not link.startswith("http"):
                    link = "https:" + link if link.startswith("//") else ""

                date_span = item.find("span", class_=re.compile(r"date|time"))
                date = date_span.text.strip() if date_span else ""

                if title and len(title) > 4:
                    news_list.append({
                        "title": title,
                        "date": date,
                        "url": link,
                        "source": "同花顺",
                    })
    except Exception as e:
        print(f"[警告] 同花顺新闻获取失败: {e}")

    return news_list[:count]


def fetch_announcements_eastmoney(code: str, count: int = 10) -> list:
    """从东方财富获取公司公告。"""
    announcements = []
    try:
        # 东方财富公告 API（stock_list 使用纯代码，无市场前缀）
        url = (
            f"https://np-anotice-stock.eastmoney.com/api/security/ann"
            f"?page_size={count}&page_index=1"
            f"&ann_type=A&stock_list={code}"
            f"&f_node=0&s_node=0"
        )
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        data = resp.json()

        items = data.get("data", {}).get("list", [])
        for item in items[:count]:
            title = item.get("title_ch", "") or item.get("title", "")
            date = item.get("notice_date", "")[:10]
            art_code = item.get("art_code", "")
            link = f"https://data.eastmoney.com/notices/detail/{code}/{art_code}.html" if art_code else ""
            announcements.append({
                "title": title,
                "date": date,
                "url": link,
                "source": "东方财富",
            })
    except Exception as e:
        print(f"[警告] 东方财富公告获取失败: {e}")

    return announcements[:count]


def fetch_news_eastmoney(code: str, count: int = 10) -> list:
    """从东方财富获取个股相关新闻。"""
    news_list = []
    try:
        url = (
            f"https://search-api-web.eastmoney.com/search/jsonp"
            f"?cb=jQuery&param="
            f'{{"uid":"","keyword":"{code}","type":["cmsArticleWebOld"],'
            f'"client":"web","clientType":"web","clientVersion":"curr",'
            f'"param":{{"cmsArticleWebOld":{{"searchScope":"default",'
            f'"sort":"default","pageIndex":1,"pageSize":{count},"preTag":"","postTag":""}}}}}}'
        )
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        text = resp.text

        match = re.search(r'jQuery\((.*)\)', text, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            cms = data.get("result", {}).get("cmsArticleWebOld", [])
            items = cms if isinstance(cms, list) else cms.get("list", []) if isinstance(cms, dict) else []
            for item in items[:count]:
                title = item.get("title", "").replace("<em>", "").replace("</em>", "")
                date = item.get("date", "")[:10]
                link = item.get("url", "")
                news_list.append({
                    "title": title,
                    "date": date,
                    "url": link,
                    "source": "东方财富",
                })
    except Exception as e:
        print(f"[警告] 东方财富新闻获取失败: {e}")

    return news_list[:count]


def main():
    if len(sys.argv) < 2:
        print("用法: python3 news.py <股票代码> [数量]")
        sys.exit(1)

    code = sys.argv[1].strip()
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    if not code.isdigit() or len(code) != 6:
        print(f"[错误] 无效的股票代码: {code}")
        sys.exit(1)

    print(f"[信息] 正在获取 {code} 的新闻和公告...")

    # 公司公告
    announcements = fetch_announcements_eastmoney(code, count)
    # 新闻
    news_em = fetch_news_eastmoney(code, count)
    news_ths = fetch_news_10jqka(code, count)

    # 显示公告
    print(f"\n=== 公司公告（{len(announcements)} 条）===")
    if announcements:
        for i, item in enumerate(announcements, 1):
            date_str = f"[{item['date']}] " if item['date'] else ""
            print(f"  {i}. {date_str}{item['title']}")
            if item['url']:
                print(f"     {item['url']}")
    else:
        print("  暂无公告")

    # 合并新闻并去重
    all_news = news_em + news_ths
    seen_titles = set()
    unique_news = []
    for item in all_news:
        short_title = item["title"][:20]
        if short_title not in seen_titles:
            seen_titles.add(short_title)
            unique_news.append(item)

    print(f"\n=== 相关新闻（{len(unique_news)} 条）===")
    if unique_news:
        for i, item in enumerate(unique_news[:count], 1):
            date_str = f"[{item['date']}] " if item['date'] else ""
            source_str = f"（{item['source']}）" if item.get('source') else ""
            print(f"  {i}. {date_str}{item['title']}{source_str}")
            if item['url']:
                print(f"     {item['url']}")
    else:
        print("  暂无相关新闻")

    print(f"\n{'=' * 55}")
    print("提示: 可以让 Claude 对以上新闻进行情绪分析和关键事件解读。")


if __name__ == "__main__":
    main()
