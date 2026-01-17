from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class IntegratorFee:
    recipient: str
    value_in_percentage: Decimal


@dataclass
class InvestmentParameters:
    slippage_tolerance_in_percentage: Decimal


@dataclass
class InvestmentParametersWithFee(InvestmentParameters):
    integrator_fee: Optional[IntegratorFee] = None
