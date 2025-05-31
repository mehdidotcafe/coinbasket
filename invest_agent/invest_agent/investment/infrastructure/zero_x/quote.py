from typing import Any, Dict, Literal, Optional, Union
from invest_agent.investment.infrastructure.zero_x.fee import Fees
from pydantic import BaseModel


class Permit2(BaseModel):
    eip712: Optional[Dict[str, Any]] = None


class Transaction(BaseModel):
    to: str
    data: str
    gas: Optional[str]
    gasPrice: str
    value: str


class InsufficientLiquidityQuote(BaseModel):
    liquidityAvailable: Literal[False]


class Quote(BaseModel):
    liquidityAvailable: Literal[True]
    permit2: Optional[Permit2] = None
    transaction: Transaction
    buyAmount: str
    buyToken: str
    sellAmount: str
    sellToken: str
    fees: Fees


QuoteResult = Union[InsufficientLiquidityQuote, Quote]
