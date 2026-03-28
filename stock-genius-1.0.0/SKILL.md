---
name: stock-genius
description: A股智能助手。管理自选股、查看实时行情、个股详情分析（市盈率/市净率/市值/财务指标）、涨跌幅排行榜、财报摘要解读、新闻公告聚合、A股热点新闻排行榜。当用户提到股票、行情、自选股、涨跌、财报、公告等关键词时触发。
---

# Stock Genius - A股智能助手

一个功能全面的A股市场分析和自选股管理工具。

## 重要：首次使用

首次使用时，请运行安装脚本：
```bash
cd $SKILL_DIR && bash scripts/install.sh
```

所有 Python 脚本需要在 `scripts/` 目录下运行：
```bash
cd $SKILL_DIR/scripts && python3 <脚本名>.py <参数>
```

## 功能一览

### 1. 自选股管理

**添加股票到自选股：**
```bash
cd $SKILL_DIR/scripts && python3 add_stock.py <6位代码> [名称]
```
- 示例：`python3 add_stock.py 600519`
- 不提供名称时自动从网络获取

**从自选股中删除：**
```bash
cd $SKILL_DIR/scripts && python3 remove_stock.py <代码>
```

**查看自选股列表：**
```bash
cd $SKILL_DIR/scripts && python3 list_stocks.py
```

**清空自选股：**
```bash
cd $SKILL_DIR/scripts && python3 clear_watchlist.py
```

**搜索股票（支持模糊搜索）：**
```bash
cd $SKILL_DIR/scripts && python3 query_stock.py <代码或名称>
```
- 支持6位代码精确查询
- 支持中文名称模糊搜索（如 `query_stock.py 茅台`）

### 2. 实时行情

**查询指定股票实时行情：**
```bash
cd $SKILL_DIR/scripts && python3 realtime_quote.py <代码1> [代码2] [代码3]
```
- 返回：最新价、涨跌幅、开盘/最高/最低、成交量、成交额

**自选股行情概览（批量查询+排序）：**
```bash
cd $SKILL_DIR/scripts && python3 watchlist_overview.py [排序字段]
```
- 排序字段可选：`change_pct`（涨跌幅，默认）、`amount`（成交额）、`volume`（成交量）、`current`（股价）
- 以表格形式展示所有自选股行情，并汇总涨跌数量

### 3. 个股详情分析

```bash
cd $SKILL_DIR/scripts && python3 stock_detail.py <代码>
```
- **价格信息**：最新价、涨跌、开盘/最高/最低、振幅
- **交易信息**：成交量、成交额、换手率、量比
- **估值信息**：市盈率、市净率、总市值/流通市值、52周高低点
- **财务摘要**：营收、净利润、每股收益、ROE、毛利率、资产负债率

### 4. 涨跌幅排行榜

```bash
cd $SKILL_DIR/scripts && python3 ranking.py [gainers|losers] [数量]
```
- 默认：涨幅榜 TOP 20
- `python3 ranking.py losers 10` 查看跌幅榜前10名
- 显示：代码、名称、最新价、涨跌幅、换手率、成交额

### 5. 财报摘要

```bash
cd $SKILL_DIR/scripts && python3 financial_report.py <代码> [期数]
```
- 默认：最近4期财报
- 返回结构化财务数据，供 Claude 分析解读
- 包含：营收、净利润、毛利率、净利率、ROE、资产负债率、每股指标等
- **获取数据后，Claude 应主动分析关键趋势、增长率变化和潜在风险**

### 6. 新闻公告聚合 / 热点新闻排行榜

```bash
cd $SKILL_DIR/scripts && python3 news.py <代码> [数量]
cd $SKILL_DIR/scripts && python3 news.py hot [数量]
```
- 聚合来自东方财富和同花顺的多源信息
- 公司公告（含链接）
- 相关新闻报道（含来源和链接）
- 支持查询东方财富 A 股热点新闻/话题排行榜（含摘要、阅读量、讨论量、链接）
- **获取数据后，Claude 应主动分析新闻情绪和关键事件影响**

## 触发规则

当用户出现以下情况时使用本技能：
- 提到股票代码（如 600519、000001 等6位数字）
- 询问股价、行情、涨跌情况
- 要求添加/删除/查看自选股
- 查看今日涨幅榜或跌幅榜
- 查看 A 股热点新闻、热点话题或新闻热榜
- 要求分析个股基本面或财务状况
- 询问某只股票的新闻或公告
- 提到以下关键词：A股、股票、行情、自选股、涨跌、涨停、跌停、市盈率、市净率、财报、公告、利润、营收、热点新闻、新闻热榜、热点话题

## 数据来源

| 来源 | 用途 |
|------|------|
| 新浪财经 | 实时行情（快速稳定） |
| 同花顺(10jqka) | 股票搜索、名称获取、新闻 |
| 东方财富 | 排行榜、个股详情、公告、新闻、热点新闻/话题榜 |
| AkShare | 财报数据、财务分析指标 |

## 数据存储

- 自选股文件：`~/.stock_genius/watchlist.txt`
- 格式：每行 `股票代码|股票名称`（UTF-8 编码）

## 依赖

- Python 3.8+
- requests
- beautifulsoup4
- akshare

## 注意事项

- 股票代码必须为6位数字（如 600519 代表贵州茅台）
- 市场前缀自动识别：6xx=沪市、0xx/3xx=深市、8xx/4xx=北交所
- 实时数据可能有1-3分钟延迟
- 财务数据取决于公司报告发布周期
- 所有功能均需要网络连接
