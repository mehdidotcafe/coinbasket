from dataclasses import dataclass


@dataclass
class Fees:
    chain_fee: int
    provider_fee: int | None = None
    service_fee: int | None = None
