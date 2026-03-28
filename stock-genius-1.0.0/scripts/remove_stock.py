"""
Stock Genius - 从自选股中删除股票
用法: python3 remove_stock.py <股票代码>
"""
import sys
from config import load_watchlist, save_watchlist


def main():
    if len(sys.argv) < 2:
        print("用法: python3 remove_stock.py <股票代码>")
        sys.exit(1)

    code = sys.argv[1].strip()
    watchlist = load_watchlist()
    new_list = [(c, n) for c, n in watchlist if c != code]

    if len(new_list) == len(watchlist):
        print(f"[提示] 自选股中未找到 {code}")
        return

    removed = [(c, n) for c, n in watchlist if c == code][0]
    save_watchlist(new_list)
    print(f"[成功] 已从自选股中删除 {removed[0]}（{removed[1]}）")
    print(f"[信息] 自选股中还剩 {len(new_list)} 只股票")


if __name__ == "__main__":
    main()
