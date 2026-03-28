"""
Stock Genius - 个股详情分析（基本面 + 核心指标）
用法: python3 stock_detail.py <股票代码>

获取: 市盈率、市净率、总市值、换手率、52周高低点、营收、净利润、ROE 等。
"""
import sys
import requests
from config import get_market_prefix, SINA_API, SINA_HEADERS, HEADERS, TIMEOUT


def fetch_spot_eastmoney(code: str) -> dict:
    """从东方财富 API 获取实时行情详情（快速，单只股票）。"""
    detail = {}
    try:
        prefix = "1" if code.startswith("6") else "0"
        secid = f"{prefix}.{code}"
        url = (
            f"https://push2.eastmoney.com/api/qt/stock/get"
            f"?secid={secid}"
            f"&fields=f43,f44,f45,f46,f47,f48,f50,f51,f52,f55,f57,f58,"
            f"f60,f116,f117,f162,f167,f168,f169,f170,f171"
        )
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        data = resp.json().get("data", {})
        if not data:
            return detail

        detail["code"] = data.get("f57", code)
        detail["name"] = data.get("f58", "")
        detail["current_price"] = (data.get("f43", 0) or 0) / 100
        detail["change"] = (data.get("f169", 0) or 0) / 100
        detail["change_pct"] = (data.get("f170", 0) or 0) / 100
        detail["open"] = (data.get("f46", 0) or 0) / 100
        detail["high"] = (data.get("f44", 0) or 0) / 100
        detail["low"] = (data.get("f45", 0) or 0) / 100
        detail["yesterday_close"] = (data.get("f60", 0) or 0) / 100
        detail["volume"] = data.get("f47", 0) or 0  # 手
        detail["amount"] = data.get("f48", 0) or 0  # 元
        detail["amplitude"] = (data.get("f171", 0) or 0) / 100
        detail["turnover_rate"] = (data.get("f168", 0) or 0) / 100
        detail["pe_ratio"] = (data.get("f162", 0) or 0) / 100
        detail["pb_ratio"] = (data.get("f167", 0) or 0) / 1000
        detail["total_market_cap"] = data.get("f116", 0) or 0
        detail["circulating_market_cap"] = data.get("f117", 0) or 0
        detail["volume_ratio"] = (data.get("f50", 0) or 0) / 100
        detail["high_52w"] = (data.get("f51", 0) or 0) / 100
        detail["low_52w"] = (data.get("f52", 0) or 0) / 100
    except Exception as e:
        print(f"[警告] 获取行情数据失败: {e}")

    return detail


def fetch_financial_ths(code: str) -> dict:
    """通过 akshare 从同花顺获取最新财务摘要。"""
    fin = {}
    try:
        import akshare as ak
        df = ak.stock_financial_abstract_ths(symbol=code)
        if df is None or df.empty:
            return fin

        latest_period = df["report_date"].iloc[0]
        fin["financial_period"] = str(latest_period)

        latest_df = df[df["report_date"] == latest_period]

        metric_map = {
            "operating_income_total": "revenue",
            "parent_holder_net_profit": "net_profit",
            "basic_eps": "eps",
            "index_weighted_avg_roe": "roe",
            "sale_gross_margin": "gross_margin",
            "assets_debt_ratio": "debt_ratio",
            "calc_per_net_assets": "net_assets_per_share",
        }

        for _, row in latest_df.iterrows():
            metric = row.get("metric_name", "")
            if metric in metric_map:
                val = row.get("value")
                try:
                    fin[metric_map[metric]] = float(val) if val and str(val) not in ("nan", "--", "") else None
                except (ValueError, TypeError):
                    fin[metric_map[metric]] = None
    except Exception as e:
        print(f"[警告] 获取财务数据失败: {e}")
    return fin


def format_detail(d: dict) -> str:
    """格式化个股详情输出。"""
    lines = []
    lines.append(f"=== {d.get('code', '')} {d.get('name', '')} 个股详情 ===")
    lines.append("")

    lines.append("【价格信息】")
    lines.append(f"  最新价:     {d.get('current_price', 'N/A')}")
    if d.get("change_pct") is not None:
        sign = "+" if d["change_pct"] >= 0 else ""
        lines.append(f"  涨跌:       {sign}{d.get('change', 0):.2f}（{sign}{d['change_pct']:.2f}%）")
    lines.append(f"  开盘: {d.get('open', 'N/A')}  |  最高: {d.get('high', 'N/A')}  |  最低: {d.get('low', 'N/A')}")
    lines.append(f"  昨收:       {d.get('yesterday_close', 'N/A')}")
    if d.get("amplitude") is not None:
        lines.append(f"  振幅:       {d['amplitude']:.2f}%")
    lines.append("")

    lines.append("【交易信息】")
    if d.get("volume") is not None:
        lines.append(f"  成交量:     {d['volume']} 手")
    if d.get("amount") is not None:
        lines.append(f"  成交额:     {d['amount']/100000000:.2f} 亿元")
    if d.get("turnover_rate") is not None:
        lines.append(f"  换手率:     {d['turnover_rate']:.2f}%")
    if d.get("volume_ratio") is not None:
        lines.append(f"  量比:       {d['volume_ratio']:.2f}")
    lines.append("")

    lines.append("【估值信息】")
    if d.get("pe_ratio") is not None:
        lines.append(f"  市盈率(TTM): {d['pe_ratio']:.2f}")
    if d.get("pb_ratio") is not None:
        lines.append(f"  市净率:      {d['pb_ratio']:.2f}")
    if d.get("total_market_cap") is not None:
        lines.append(f"  总市值:      {d['total_market_cap']/100000000:.2f} 亿元")
    if d.get("circulating_market_cap") is not None:
        lines.append(f"  流通市值:    {d['circulating_market_cap']/100000000:.2f} 亿元")
    if d.get("high_52w") is not None and d["high_52w"] > 0:
        lines.append(f"  52周最高:    {d['high_52w']:.2f}")
    if d.get("low_52w") is not None and d["low_52w"] > 0:
        lines.append(f"  52周最低:    {d['low_52w']:.2f}")
    lines.append("")

    if d.get("financial_period"):
        lines.append(f"【财务摘要 - {d['financial_period']}】")
        if d.get("revenue") is not None:
            rev = d["revenue"]
            lines.append(f"  营业总收入:  {rev/100000000:.2f} 亿元" if isinstance(rev, (int, float)) and rev > 10000 else f"  营业总收入:  {rev}")
        if d.get("net_profit") is not None:
            np_ = d["net_profit"]
            lines.append(f"  归母净利润:  {np_/100000000:.2f} 亿元" if isinstance(np_, (int, float)) and abs(np_) > 10000 else f"  归母净利润:  {np_}")
        if d.get("eps") is not None:
            lines.append(f"  每股收益:    {d['eps']}")
        if d.get("roe") is not None:
            lines.append(f"  ROE:         {d['roe']}%")
        if d.get("gross_margin") is not None:
            lines.append(f"  毛利率:      {d['gross_margin']}%")
        if d.get("debt_ratio") is not None:
            lines.append(f"  资产负债率:  {d['debt_ratio']}%")
        if d.get("net_assets_per_share") is not None:
            lines.append(f"  每股净资产:  {d['net_assets_per_share']}")
        lines.append("")

    lines.append("=" * 50)
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 stock_detail.py <股票代码>")
        sys.exit(1)

    code = sys.argv[1].strip()
    if not code.isdigit() or len(code) != 6:
        print(f"[错误] 无效的股票代码: {code}")
        sys.exit(1)

    # 快速获取: 东方财富行情数据
    detail = fetch_spot_eastmoney(code)
    if not detail:
        detail = {"code": code, "name": ""}

    # 较慢获取: 同花顺财务摘要
    fin = fetch_financial_ths(code)
    detail.update(fin)

    print(format_detail(detail))


if __name__ == "__main__":
    main()
