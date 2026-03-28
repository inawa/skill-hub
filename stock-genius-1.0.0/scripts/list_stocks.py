"""
Stock Genius - 查看自选股列表
用法: python3 list_stocks.py
"""
from config import load_watchlist


def main():
    watchlist = load_watchlist()
    if not watchlist:
        print("[提示] 自选股列表为空，请使用 add_stock.py 添加股票")
        return

    print(f"=== 自选股列表（共 {len(watchlist)} 只）===")
    for i, (code, name) in enumerate(watchlist, 1):
        print(f"  {i}. {code} - {name}")
    print("=" * 35)


if __name__ == "__main__":
    main()
