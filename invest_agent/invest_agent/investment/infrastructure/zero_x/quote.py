from typing import Any, Dict, Optional
from pydantic import BaseModel


class Permit2(BaseModel):
    eip712: Optional[Dict[str, Any]] = None


class Transaction(BaseModel):
    to: str
    data: str
    gas: Optional[str]
    gasPrice: str
    value: str


class Fee(BaseModel):
    amount: str
    token: str
    type: str


class Fees(BaseModel):
    integratorFee: Optional[Fee] = None
    zeroExFee: Optional[Fee] = None
    gasFee: Optional[Fee] = None


class Quote(BaseModel):
    liquidityAvailable: bool
    permit2: Optional[Permit2] = None
    transaction: Transaction
    buyAmount: str
    buyToken: str
    sellAmount: str
    sellToken: str
    fees: Fees
