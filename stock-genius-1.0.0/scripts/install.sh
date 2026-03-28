#!/bin/bash
# Stock Genius - 安装脚本

DATA_DIR="$HOME/.stock_genius"
WATCHLIST_FILE="$DATA_DIR/watchlist.txt"

echo "=== Stock Genius 安装程序 ==="

# 创建数据目录
mkdir -p "$DATA_DIR"
echo "[完成] 数据目录已创建: $DATA_DIR"

# 创建自选股文件
if [ ! -f "$WATCHLIST_FILE" ]; then
    touch "$WATCHLIST_FILE"
    echo "[完成] 自选股文件已创建: $WATCHLIST_FILE"
else
    echo "[完成] 自选股文件已存在"
fi

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 python3，请先安装 Python 3.8+"
    exit 1
fi

# 检查依赖包
MISSING=""
for pkg in requests beautifulsoup4 akshare; do
    python3 -c "import $(echo $pkg | sed 's/-/_/g' | sed 's/beautifulsoup4/bs4/')" 2>/dev/null
    if [ $? -ne 0 ]; then
        MISSING="$MISSING $pkg"
    fi
done

if [ -n "$MISSING" ]; then
    echo "[信息] 正在安装缺失的依赖包:$MISSING"
    pip3 install $MISSING
    echo "[完成] 依赖包安装完成"
else
    echo "[完成] 所有依赖包已就绪"
fi

echo "=== 安装完成 ==="
