from typing import Any, Dict, Literal, Optional, Union, Annotated
from api.investment.infrastructure.zero_x.fee import Fees
from pydantic import BaseModel, Field, RootModel


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


class QuoteResult(RootModel[Any]):
    root: Annotated[
        Union[Quote, InsufficientLiquidityQuote],
        Field(discriminator="liquidityAvailable"),
    ]
