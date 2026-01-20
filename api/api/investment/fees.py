from dataclasses import dataclass
import json

from api.chain.balance import BalanceAtomic


@dataclass
class Fees:
    gas_fee: BalanceAtomic | None = None
    provider_fee: BalanceAtomic | None = None
    platform_fee: BalanceAtomic | None = None

    def serialize(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            "gas_fee": self.gas_fee.to_dict() if self.gas_fee else None,
            "provider_fee": self.provider_fee.to_dict() if self.provider_fee else None,
            "platform_fee": self.platform_fee.to_dict() if self.platform_fee else None,
        }
