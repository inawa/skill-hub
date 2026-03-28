"""
Stock Genius - 清空自选股列表
用法: python3 clear_watchlist.py
"""
from config import load_watchlist, save_watchlist


def main():
    watchlist = load_watchlist()
    if not watchlist:
        print("[提示] 自选股列表已经是空的")
        return

    count = len(watchlist)
    save_watchlist([])
    print(f"[成功] 已清空自选股列表（共删除 {count} 只股票）")


if __name__ == "__main__":
    main()
