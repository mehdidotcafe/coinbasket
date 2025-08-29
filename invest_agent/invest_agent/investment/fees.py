from dataclasses import dataclass
import json


@dataclass
class Fees:
    chain_fee: int
    provider_fee: int | None = None
    service_fee: int | None = None

    def serialize(self):
        return json.dumps(
            {
                "chain_fee": self.chain_fee,
                "provider_fee": self.provider_fee,
                "service_fee": self.service_fee,
            }
        )

    @staticmethod
    def deserialize(fees_as_json: str) -> "Fees":
        fees_data = json.loads(fees_as_json)
        return Fees(
            chain_fee=fees_data["chain_fee"],
            provider_fee=fees_data.get("provider_fee"),
            service_fee=fees_data.get("service_fee"),
        )
