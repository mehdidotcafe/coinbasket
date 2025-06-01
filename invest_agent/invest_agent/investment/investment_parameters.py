from dataclasses import dataclass
from decimal import Decimal


@dataclass
class InvestmentParameters:
    slippage_tolerance_in_percentage: Decimal
