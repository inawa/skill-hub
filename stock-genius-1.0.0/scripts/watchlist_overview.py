"""
Stock Genius - 自选股行情概览（批量行情 + 排序）
用法: python3 watchlist_overview.py [排序字段]
  排序字段: change_pct（默认，涨跌幅）、amount（成交额）、volume（成交量）、current（股价）
"""
import sys
from config import load_watchlist
from realtime_quote import fetch_realtime


def main():
    sort_by = sys.argv[1] if len(sys.argv) > 1 else "change_pct"

    watchlist = load_watchlist()
    if not watchlist:
        print("[提示] 自选股列表为空，请先添加股票")
        return

    codes = [c for c, n in watchlist]
    results = fetch_realtime(codes)

    if not results:
        print("[提示] 未返回数据，可能已收盘")
        return

    # 排序
    sort_labels = {
        "change_pct": "涨跌幅",
        "amount": "成交额",
        "volume": "成交量",
        "current": "股价",
    }
    if sort_by not in sort_labels:
        sort_by = "change_pct"
    results.sort(key=lambda x: x.get(sort_by, 0), reverse=True)

    # 表头
    print(f"=== 自选股概览（按{sort_labels[sort_by]}排序，共 {len(results)} 只）===")
    print(f"{'序号':<4}{'代码':<8}{'名称':<10}{'最新价':<10}{'涨跌幅':<10}{'成交量(手)':<12}{'成交额(万)':<12}")
    print("-" * 66)

    for i, q in enumerate(results, 1):
        sign = "+" if q["change_pct"] >= 0 else ""
        pct_str = f"{sign}{q['change_pct']:.2f}%"
        amount_w = f"{q['amount']/10000:.1f}"
        print(f"{i:<4}{q['code']:<8}{q['name']:<10}{q['current']:<10.2f}{pct_str:<10}{q['volume']:<12}{amount_w:<12}")

    print("=" * 66)

    # 汇总
    up = sum(1 for q in results if q["change_pct"] > 0)
    down = sum(1 for q in results if q["change_pct"] < 0)
    flat = len(results) - up - down
    print(f"汇总: {up} 只上涨, {down} 只下跌, {flat} 只平盘")


if __name__ == "__main__":
    main()
