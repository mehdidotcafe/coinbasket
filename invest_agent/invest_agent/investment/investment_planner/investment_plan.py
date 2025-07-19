from dataclasses import dataclass

from invest_agent.chain.asset_balance import AssetBalance


@dataclass
class InvestmentPlanStep:
    buy_balance: AssetBalance
    sell_balance: AssetBalance


@dataclass
class InvestmentPlan:
    steps: list[InvestmentPlanStep]
