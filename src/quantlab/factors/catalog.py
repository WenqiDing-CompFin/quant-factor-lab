"""Factor catalog — the starting point of factor selection.

How to read this file (Lesson 01–02):
1. Every factor needs an economic story (why should it earn return?)
2. Every factor needs a precise definition (how is it computed?)
3. Selection = story + empirical evidence (IC / layer returns), not vibes
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FactorSpec:
    name: str
    category: str  # value / momentum / quality / size / risk / liquidity
    direction: int  # +1: higher → expected higher return; -1: opposite
    description_zh: str
    description_en: str
    why_it_might_work: str
    common_pitfalls: str


FACTOR_CATALOG: dict[str, FactorSpec] = {
    "ep": FactorSpec(
        name="ep",
        category="value",
        direction=1,
        description_zh="盈利收益率 E/P（用 1/PE 近似）",
        description_en="Earnings yield ≈ 1/PE",
        why_it_might_work="便宜的盈利相对更可能被市场低估（价值溢价）",
        common_pitfalls="亏损股 PE 失真；行业差异大，常需行业中性",
    ),
    "bp": FactorSpec(
        name="bp",
        category="value",
        direction=1,
        description_zh="账面市值比 B/P（用 1/PB 近似）",
        description_en="Book-to-price ≈ 1/PB",
        why_it_might_work="经典 Fama–French HML 价值因子",
        common_pitfalls="重资产行业天然更高；会计政策影响账面价值",
    ),
    "momentum_12_1": FactorSpec(
        name="momentum_12_1",
        category="momentum",
        direction=1,
        description_zh="12-1 动量（中期趋势，跳过最近1个月）",
        description_en="12-1 momentum (skip most recent month)",
        why_it_might_work="趋势延续 / 反应不足；A股中期动量偶发有效",
        common_pitfalls="A股短期常反转；拥挤交易会失效",
    ),
    "reverse_1m": FactorSpec(
        name="reverse_1m",
        category="momentum",
        direction=1,
        description_zh="1个月反转（做多近期弱势）",
        description_en="1-month reversal (long recent losers)",
        why_it_might_work="A股散户博弈下短期过度反应更常见",
        common_pitfalls="与动量冲突；换手高、成本敏感",
    ),
    "volatility_20": FactorSpec(
        name="volatility_20",
        category="risk",
        direction=-1,
        description_zh="近20日波动率（低波更好）",
        description_en="20-day volatility (low-vol premium)",
        why_it_might_work="低波异象：高风险未必高收益",
        common_pitfalls="熊市可能失效；需控制流动性",
    ),
    "turnover_20": FactorSpec(
        name="turnover_20",
        category="liquidity",
        direction=-1,
        description_zh="换手率（偏高换手常偏弱）",
        description_en="Turnover (high turnover often underperforms)",
        why_it_might_work="过度交易 / 情绪过热惩罚",
        common_pitfalls="与市值、波动高度相关，需中性化",
    ),
    "roe": FactorSpec(
        name="roe",
        category="quality",
        direction=1,
        description_zh="净资产收益率（质量）",
        description_en="Return on equity (quality)",
        why_it_might_work="高质量盈利更可持续，估值更易扩张",
        common_pitfalls="高 ROE 可能已贵；需结合估值",
    ),
    "size_log_mcap": FactorSpec(
        name="size_log_mcap",
        category="size",
        direction=-1,
        description_zh="对数市值（小盘效应：市值越小分越高）",
        description_en="Log market cap (small-cap tilt after sign flip)",
        why_it_might_work="小盘溢价 / 流动性补偿（争议大）",
        common_pitfalls="A股小盘拥挤；容量与退市风险",
    ),
}


def list_factors(category: str | None = None) -> list[FactorSpec]:
    specs = list(FACTOR_CATALOG.values())
    if category:
        specs = [s for s in specs if s.category == category]
    return specs
