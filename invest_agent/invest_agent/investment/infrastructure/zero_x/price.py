from typing import Optional
from invest_agent.investment.infrastructure.zero_x.fee import Fees
from pydantic import BaseModel


class Allowance(BaseModel):
    spender: str


class Issues(BaseModel):
    allowance: Optional[Allowance] = None


class Price(BaseModel):
    issues: Issues
    buyAmount: str
    buyToken: str
    sellAmount: str
    sellToken: str
    fees: Fees
