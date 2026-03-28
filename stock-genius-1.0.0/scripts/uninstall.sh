#!/bin/bash
# Stock Genius - 卸载脚本

DATA_DIR="$HOME/.stock_genius"

echo "=== Stock Genius 卸载程序 ==="

if [ -d "$DATA_DIR" ]; then
    rm -rf "$DATA_DIR"
    echo "[完成] 已删除数据目录: $DATA_DIR"
else
    echo "[提示] 未找到数据目录"
fi

echo "=== 卸载完成 ==="
