"""
Stock Genius - 涨跌幅排行榜
用法: python3 ranking.py [gainers|losers] [数量]
  gainers: 涨幅榜（默认）
  losers: 跌幅榜
  数量: 默认20
"""
import sys
import requests
from config import HEADERS, TIMEOUT


def get_ranking(direction: str = "gainers", count: int = 20):
    """从东方财富 API 获取涨跌幅排行榜。"""
    label = "涨幅榜" if direction == "gainers" else "跌幅榜"
    print(f"[信息] 正在获取{label} TOP {count}...")

    try:
        order = "f3:desc" if direction == "gainers" else "f3:asc"
        url = (
            f"https://push2.eastmoney.com/api/qt/clist/get"
            f"?pn=1&pz={count}&po=1&np=1&fltt=2&invt=2"
            f"&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23"
            f"&fields=f2,f3,f4,f5,f6,f8,f12,f14"
        )
        if direction == "losers":
            url = url.replace("&po=1", "&po=0")

        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        data = resp.json()

        items = data.get("data", {}).get("diff", [])
        if not items:
            print("[错误] 未获取到行情数据")
            return

        print(f"\n=== {label}（TOP {count}）===")
        print(f"{'序号':<4}{'代码':<8}{'名称':<10}{'最新价':<10}{'涨跌幅':<10}{'换手率%':<10}{'成交额(亿)':<10}")
        print("-" * 62)

        for i, item in enumerate(items[:count], 1):
            code = item.get("f12", "")
            name = str(item.get("f14", ""))[:8]
            price = item.get("f2", 0) or 0
            pct = item.get("f3", 0) or 0
            turnover = item.get("f8", 0) or 0
            amount = item.get("f6", 0) or 0
            amount_b = amount / 100000000

            sign = "+" if pct >= 0 else ""
            pct_str = f"{sign}{pct:.2f}%"

            try:
                print(f"{i:<4}{code:<8}{name:<10}{price:<10.2f}{pct_str:<10}{turnover:<10.2f}{amount_b:<10.2f}")
            except (TypeError, ValueError):
                print(f"{i:<4}{code:<8}{name:<10}{'N/A':<10}{pct_str:<10}{'N/A':<10}{'N/A':<10}")

        print("=" * 62)

    except Exception as e:
        print(f"[错误] 获取排行榜失败: {e}")


def main():
    direction = sys.argv[1] if len(sys.argv) > 1 else "gainers"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    if direction not in ("gainers", "losers"):
        print("用法: python3 ranking.py [gainers|losers] [数量]")
        print("  gainers: 涨幅榜（默认）")
        print("  losers:  跌幅榜")
        sys.exit(1)

    get_ranking(direction, count)


if __name__ == "__main__":
    main()
