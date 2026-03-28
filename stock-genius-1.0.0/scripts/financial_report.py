"""
Stock Genius - 财报摘要
用法: python3 financial_report.py <股票代码> [期数]
  期数: 显示最近几期财报（默认: 4）

获取关键财务指标数据，供 Claude 分析解读。
"""
import sys
import requests


def get_stock_name(code: str) -> str:
    """通过新浪 API 获取股票名称。"""
    from config import get_market_prefix, SINA_API, SINA_HEADERS, TIMEOUT
    try:
        prefixed = get_market_prefix(code)
        resp = requests.get(SINA_API + prefixed, headers=SINA_HEADERS, timeout=TIMEOUT)
        resp.encoding = "gbk"
        for line in resp.text.strip().split("\n"):
            if "=" in line:
                data = line.split("=", 1)[1].strip('";\n').split(",")
                if len(data) > 0:
                    return data[0]
    except Exception:
        pass
    return code


def get_financial_report(code: str, periods: int = 4):
    """通过 akshare 获取财报数据。"""
    import akshare as ak

    print(f"[信息] 正在获取 {code} 最近 {periods} 期财报数据...")

    name = get_stock_name(code)
    result = {"code": code, "name": name}

    # 需要提取的关键指标
    key_metrics = {
        "operating_income_total": "营业总收入",
        "parent_holder_net_profit": "归母净利润",
        "index_deduct_holder_net_profit": "扣非净利润",
        "basic_eps": "每股收益(EPS)",
        "index_weighted_avg_roe": "加权ROE(%)",
        "index_full_diluted_roe": "摊薄ROE(%)",
        "sale_gross_margin": "毛利率(%)",
        "sale_net_interest_ratio": "净利率(%)",
        "assets_debt_ratio": "资产负债率(%)",
        "current_ratio": "流动比率",
        "quick_ratio": "速动比率",
        "calc_per_net_assets": "每股净资产",
        "per_undistributed_profits": "每股未分配利润",
        "per_capital_reserve": "每股公积金",
        "index_per_operating_cash_flow_net": "每股经营现金流",
        "inventory_turnover_ratio": "存货周转率",
        "receive_accounts_turnover_days": "应收账款周转天数",
        "calculate_operating_income_total_yoy_growth_ratio": "营收同比增长率(%)",
        "calculate_parent_holder_net_profit_yoy_growth_ratio": "净利润同比增长率(%)",
        "deduct_net_profit_yoy_growth_ratio": "扣非净利润同比增长率(%)",
    }

    try:
        df = ak.stock_financial_abstract_ths(symbol=code)
        if df is None or df.empty:
            print("[警告] 无财报数据")
            result["periods"] = []
            return result

        report_dates = sorted(df["report_date"].unique(), reverse=True)[:periods]

        periods_data = []
        for rd in report_dates:
            period_df = df[df["report_date"] == rd]
            report_name = period_df["report_name"].iloc[0] if not period_df.empty else str(rd)
            period_info = {"period": str(rd), "report_name": str(report_name), "metrics": {}}

            for _, row in period_df.iterrows():
                metric = row.get("metric_name", "")
                if metric in key_metrics:
                    val = row.get("value")
                    yoy = row.get("yoy")
                    try:
                        val_f = float(val) if val and str(val) not in ("nan", "--", "") else None
                    except (ValueError, TypeError):
                        val_f = None
                    try:
                        yoy_f = float(yoy) if yoy and str(yoy) not in ("nan", "--", "") else None
                    except (ValueError, TypeError):
                        yoy_f = None

                    period_info["metrics"][key_metrics[metric]] = {
                        "value": val_f,
                        "yoy": yoy_f,
                    }

            periods_data.append(period_info)

        result["periods"] = periods_data

    except Exception as e:
        print(f"[警告] 获取财报数据失败: {e}")
        result["periods"] = []

    return result


def format_report(data: dict) -> str:
    """格式化财报输出。"""
    lines = []
    lines.append(f"=== 财务报告: {data.get('code', '')} {data.get('name', '')} ===")
    lines.append("")

    periods = data.get("periods", [])
    if not periods:
        lines.append("[提示] 暂无财报数据")
        lines.append("=" * 55)
        return "\n".join(lines)

    for p in periods:
        lines.append(f"--- {p.get('report_name', '')}（{p.get('period', '')}）---")
        metrics = p.get("metrics", {})
        for name, info in metrics.items():
            val = info.get("value")
            yoy = info.get("yoy")
            if val is None:
                continue

            # 大数字以亿元显示
            if "营业总收入" in name or "净利润" in name:
                if isinstance(val, (int, float)) and abs(val) > 100000:
                    val_str = f"{val/100000000:.2f} 亿元"
                else:
                    val_str = f"{val}"
            else:
                val_str = f"{val:.4f}" if isinstance(val, float) else str(val)

            yoy_str = f"（同比: {yoy:+.2%}）" if yoy is not None else ""
            lines.append(f"  {name}: {val_str}{yoy_str}")
        lines.append("")

    lines.append("=" * 55)
    lines.append("")
    lines.append("提示: 可以让 Claude 对以上数据进行趋势分析、风险评估和亮点解读。")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 financial_report.py <股票代码> [期数]")
        sys.exit(1)

    code = sys.argv[1].strip()
    periods = int(sys.argv[2]) if len(sys.argv) > 2 else 4

    if not code.isdigit() or len(code) != 6:
        print(f"[错误] 无效的股票代码: {code}")
        sys.exit(1)

    data = get_financial_report(code, periods)
    print(format_report(data))


if __name__ == "__main__":
    main()
