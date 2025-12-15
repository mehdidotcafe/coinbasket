from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from api.protocol.token import Token


@dataclass
class IntegratorFee:
    recipient: str
    value_in_percentage: Decimal
    token: Token


@dataclass
class InvestmentParameters:
    slippage_tolerance_in_percentage: Decimal
    integrator_fee: Optional[IntegratorFee] = None
