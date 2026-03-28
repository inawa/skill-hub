"""
Stock Genius - 新闻公告聚合
用法:
  python3 news.py <股票代码> [数量]
  python3 news.py hot [数量]

从多个来源聚合个股最新新闻和公司公告，
或查询 A 股热点新闻/话题排行榜。
"""
import sys
import re
import json
import requests
from bs4 import BeautifulSoup
from config import HEADERS, TIMEOUT


HOT_NEWS_ALIASES = {"hot", "rank", "hotrank"}


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


def normalize_url(url: str, base_url: str = "") -> str:
    """补全相对链接。"""
    if not url:
        return ""
    if url.startswith("http"):
        return url
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("/") and base_url:
        return base_url.rstrip("/") + url
    return ""


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


def fetch_hot_news_eastmoney(count: int = 10) -> list:
    """从东方财富热门话题页提取热点新闻/话题排行榜。"""
    hot_list = []
    try:
        url = "https://caifuhao.eastmoney.com/hot"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        items = soup.select(".panel.hot_topic .topic_list .item")
        for item in items[:count]:
            title_tag = item.select_one(".title a")
            desc_tag = item.select_one(".desc")
            info_spans = item.select(".info span")

            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            desc = desc_tag.get_text(" ", strip=True) if desc_tag else ""
            link = normalize_url(title_tag.get("href", ""), "https://caifuhao.eastmoney.com")
            read_count = ""
            discuss_count = ""

            if len(info_spans) >= 1:
                read_count = info_spans[0].get("title", "").strip() or info_spans[0].get_text(strip=True)
            if len(info_spans) >= 2:
                discuss_count = info_spans[1].get("title", "").strip() or info_spans[1].get_text(strip=True)

            if title:
                hot_list.append({
                    "title": title,
                    "summary": desc,
                    "url": link,
                    "source": "东方财富热门话题",
                    "read_count": read_count,
                    "discuss_count": discuss_count,
                })
    except Exception as e:
        print(f"[警告] 东方财富热点新闻获取失败: {e}")

    return hot_list[:count]


def parse_count(raw: str = "", default: int = 10) -> int:
    """解析条数参数。"""
    if not raw:
        return default

    try:
        count = int(raw)
    except ValueError:
        print(f"[错误] 无效的数量参数: {raw}")
        sys.exit(1)

    if count <= 0:
        print(f"[错误] 数量必须大于 0: {count}")
        sys.exit(1)

    return count


def deduplicate_news(items: list) -> list:
    """按标题去重，避免多源重复内容。"""
    seen_titles = set()
    unique_news = []

    for item in items:
        normalized_title = re.sub(r"\s+", "", item.get("title", ""))[:30]
        if normalized_title and normalized_title not in seen_titles:
            seen_titles.add(normalized_title)
            unique_news.append(item)

    return unique_news


def show_stock_news(code: str, count: int):
    """展示个股公告和新闻。"""
    print(f"[信息] 正在获取 {code} 的新闻和公告...")

    announcements = fetch_announcements_eastmoney(code, count)
    news_em = fetch_news_eastmoney(code, count)
    news_ths = fetch_news_10jqka(code, count)
    unique_news = deduplicate_news(news_em + news_ths)

    print(f"\n=== 公司公告（{len(announcements)} 条）===")
    if announcements:
        for i, item in enumerate(announcements, 1):
            date_str = f"[{item['date']}] " if item['date'] else ""
            print(f"  {i}. {date_str}{item['title']}")
            if item['url']:
                print(f"     {item['url']}")
    else:
        print("  暂无公告")

    print(f"\n=== 相关新闻（{len(unique_news)} 条）===")
    if unique_news:
        for i, item in enumerate(unique_news[:count], 1):
            date_str = f"[{item['date']}] " if item['date'] else ""
            source_str = f"（{item['source']}）" if item.get("source") else ""
            print(f"  {i}. {date_str}{item['title']}{source_str}")
            if item['url']:
                print(f"     {item['url']}")
    else:
        print("  暂无相关新闻")

    print(f"\n{'=' * 55}")
    print("提示: 可以让 Claude 对以上新闻进行情绪分析和关键事件解读。")


def show_hot_news(count: int):
    """展示 A 股热点新闻/话题排行榜。"""
    print(f"[信息] 正在获取 A 股热点新闻排行榜 TOP {count}...")
    hot_news = fetch_hot_news_eastmoney(count)

    print(f"\n=== A 股热点新闻排行榜（TOP {count}）===")
    if hot_news:
        for i, item in enumerate(hot_news, 1):
            heat_parts = []
            if item.get("read_count"):
                heat_parts.append(f"阅读 {item['read_count']}")
            if item.get("discuss_count"):
                heat_parts.append(f"讨论 {item['discuss_count']}")
            heat_str = " | ".join(heat_parts)

            print(f"  {i}. {item['title']}")
            if item.get("summary"):
                print(f"     摘要: {item['summary']}")
            if heat_str:
                print(f"     热度: {heat_str}")
            if item.get("url"):
                print(f"     {item['url']}")
    else:
        print("  暂无热点新闻数据")

    print(f"\n{'=' * 55}")
    print("提示: 可以让 Claude 继续归纳热点主线、题材轮动和情绪变化。")


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 news.py <股票代码> [数量]")
        print("  python3 news.py hot [数量]")
        sys.exit(1)

    target = sys.argv[1].strip()
    count = parse_count(sys.argv[2] if len(sys.argv) > 2 else "", 10)

    if target.lower() in HOT_NEWS_ALIASES:
        show_hot_news(count)
        return

    if not target.isdigit() or len(target) != 6:
        print(f"[错误] 无效的股票代码或命令: {target}")
        print("提示: 使用 `hot` 查询 A 股热点新闻排行榜。")
        sys.exit(1)

    show_stock_news(target, count)


if __name__ == "__main__":
    main()
