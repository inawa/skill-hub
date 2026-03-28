# Stock Genius - A股智能助手

一个功能全面的 Claude Code 技能，用于A股市场分析和自选股管理。

## 功能特性

| 功能 | 说明 |
|------|------|
| 自选股管理 | 添加/删除/查看/清空/搜索股票 |
| 实时行情 | 查看最新价、涨跌幅、成交量等 |
| 批量概览 | 自选股行情一览，支持排序 |
| 个股详情 | 市盈率、市净率、市值、财务指标 |
| 涨跌排行 | 今日涨幅榜/跌幅榜 TOP N |
| 财报摘要 | 多期财报数据，AI 智能解读 |
| 新闻聚合 | 公司公告 + 相关新闻 + A股热点新闻/话题榜 |

## 安装

### 作为 Claude Code 技能安装

1. 将此目录放到 Claude Code 可访问的位置
2. 运行安装脚本：
   ```bash
   bash scripts/install.sh
   ```

### 手动安装依赖

```bash
pip3 install requests beautifulsoup4 akshare
```

## 快速上手

```bash
cd scripts

# 添加自选股
python3 add_stock.py 600519          # 贵州茅台
python3 add_stock.py 000001          # 平安银行

# 查看自选股列表
python3 list_stocks.py

# 查看实时行情
python3 realtime_quote.py 600519 000001

# 自选股行情概览（按涨跌幅排序）
python3 watchlist_overview.py

# 个股详情分析
python3 stock_detail.py 600519

# 涨跌幅排行榜
python3 ranking.py gainers 20        # 涨幅榜前20
python3 ranking.py losers 10         # 跌幅榜前10

# 财报摘要
python3 financial_report.py 600519 4

# 新闻公告
python3 news.py 600519 10
python3 news.py hot 10            # A股热点新闻/话题榜

# 搜索股票
python3 query_stock.py 茅台
python3 query_stock.py 600519

# 删除/清空
python3 remove_stock.py 600519
python3 clear_watchlist.py
```

## 文件结构

```
stock-genius-1.0.0/
├── _meta.json                  # 技能元数据
├── SKILL.md                    # Claude 技能说明
├── README.md                   # 本文件
├── .claude/
│   └── settings.local.json     # 权限配置
└── scripts/
    ├── config.py               # 共享配置与工具函数
    ├── install.sh              # 安装脚本
    ├── uninstall.sh            # 卸载脚本
    ├── add_stock.py            # 添加自选股
    ├── remove_stock.py         # 删除自选股
    ├── list_stocks.py          # 查看自选股
    ├── clear_watchlist.py      # 清空自选股
    ├── query_stock.py          # 搜索股票
    ├── realtime_quote.py       # 实时行情
    ├── watchlist_overview.py   # 自选股概览
    ├── stock_detail.py         # 个股详情分析
    ├── ranking.py              # 涨跌幅排行榜
    ├── financial_report.py     # 财报摘要
    └── news.py                 # 新闻公告聚合 / 热点新闻排行榜
```

## 数据来源

- **新浪财经** — 实时行情（速度快、稳定）
- **东方财富** — 排行榜、个股详情、公告、新闻、热点话题榜
- **同花顺** — 股票搜索、名称获取、新闻
- **AkShare** — 财报数据、财务分析指标

## 卸载

```bash
bash scripts/uninstall.sh
```

这将删除 `~/.stock_genius/` 目录下的所有用户数据。
