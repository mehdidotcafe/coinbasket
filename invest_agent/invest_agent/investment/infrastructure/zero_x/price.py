from typing import Optional
from pydantic import BaseModel


class Allowance(BaseModel):
    spender: str


class Issues(BaseModel):
    allowance: Optional[Allowance] = None


class Price(BaseModel):
    issues: Issues
