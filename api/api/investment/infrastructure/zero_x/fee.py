from typing import Optional
from pydantic import BaseModel


class Fee(BaseModel):
    amount: str
    token: str
    type: str


class Fees(BaseModel):
    integratorFee: Optional[Fee] = None
    zeroExFee: Optional[Fee] = None
    gasFee: Optional[Fee] = None
