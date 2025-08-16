from decimal import Decimal
from typing import Any
from hexbytes import HexBytes
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import ParsedReceipt
from invest_agent.chain.infrastructure.bsc.transaction_receipt_parser import (
    BscTransactionReceiptParser,
)
from pytest import fixture, mark
from web3 import AsyncHTTPProvider, AsyncWeb3
from web3.types import TxReceipt
from protocol.fixture.token import bnb_token, cake_token


# 0.032540290120408155 BNB -> 10 CAKE
@fixture
def receipt_bnb_cake() -> dict[str, Any]:
    return {
        "type": 0,
        "status": 1,
        "cumulativeGasUsed": 144955,
        "logs": [
            {
                "address": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                "topics": [
                    HexBytes(
                        "0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x00000000000000000000000000000000000000000000000000736ed420dd6417"
                ),
                "blockHash": HexBytes(
                    "0xa332329dd84b99feb00bc83618699269bfdbaa706070f80c84a4a8d8f54afd9a"
                ),
                "blockNumber": 57684584,
                "blockTimestamp": "0x689f2c50",
                "transactionHash": HexBytes(
                    "0x535765c7fe1ca8941958355575275943211183e3a6ae95b508f2334d175d7caf"
                ),
                "transactionIndex": 0,
                "logIndex": 0,
                "removed": False,
            },
            {
                "address": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000afb2da14056725e3ba3a30dd846b6bbbd7886c56"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000008a27f6026421dc39"
                ),
                "blockHash": HexBytes(
                    "0xa332329dd84b99feb00bc83618699269bfdbaa706070f80c84a4a8d8f54afd9a"
                ),
                "blockNumber": 57684584,
                "blockTimestamp": "0x689f2c50",
                "transactionHash": HexBytes(
                    "0x535765c7fe1ca8941958355575275943211183e3a6ae95b508f2334d175d7caf"
                ),
                "transactionIndex": 0,
                "logIndex": 1,
                "removed": False,
            },
            {
                "address": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000afb2da14056725e3ba3a30dd846b6bbbd7886c56"
                    ),
                ],
                "data": HexBytes(
                    "0x00000000000000000000000000000000000000000000000000736ed420dd6417"
                ),
                "blockHash": HexBytes(
                    "0xa332329dd84b99feb00bc83618699269bfdbaa706070f80c84a4a8d8f54afd9a"
                ),
                "blockNumber": 57684584,
                "blockTimestamp": "0x689f2c50",
                "transactionHash": HexBytes(
                    "0x535765c7fe1ca8941958355575275943211183e3a6ae95b508f2334d175d7caf"
                ),
                "transactionIndex": 0,
                "logIndex": 2,
                "removed": False,
            },
            {
                "address": "0xAfB2Da14056725E3BA3a30dD846B6BBbd7886c56",
                "topics": [
                    HexBytes(
                        "0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0xffffffffffffffffffffffffffffffffffffffffffffffff75d809fd9bde23c700000000000000000000000000000000000000000000000000736ed420dd641700000000000000000000000000000000000000000e9f19c8c45200a1f3db8784000000000000000000000000000000000000000000004b9be6e9062cb3a979c2ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff20570000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000005060d53ec78"
                ),
                "blockHash": HexBytes(
                    "0xa332329dd84b99feb00bc83618699269bfdbaa706070f80c84a4a8d8f54afd9a"
                ),
                "blockNumber": 57684584,
                "blockTimestamp": "0x689f2c50",
                "transactionHash": HexBytes(
                    "0x535765c7fe1ca8941958355575275943211183e3a6ae95b508f2334d175d7caf"
                ),
                "transactionIndex": 0,
                "logIndex": 3,
                "removed": False,
            },
            {
                "address": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000b404993a0129379d1d90e5a52d06652ffd0ae7c3"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000008a27f6026421dc39"
                ),
                "blockHash": HexBytes(
                    "0xa332329dd84b99feb00bc83618699269bfdbaa706070f80c84a4a8d8f54afd9a"
                ),
                "blockNumber": 57684584,
                "blockTimestamp": "0x689f2c50",
                "transactionHash": HexBytes(
                    "0x535765c7fe1ca8941958355575275943211183e3a6ae95b508f2334d175d7caf"
                ),
                "transactionIndex": 0,
                "logIndex": 4,
                "removed": False,
            },
        ],
        "logsBloom": HexBytes(
            "0x00000000000000000000000000020000000000000000000000000010000000000000000000000000000000000002000000000000000000000000080000000000040020000240200000000008000004000000000000000002000400008000000000000000000000010000000000000000000000000000000000000010000000000000000000000000000000000020200000040001000000002000000000000000000000000000000000000000000000000000000000000000000000000000000000008002000000000000000000000000000000000000000000000000000080000000000000000000800000000000000000000008000000400000000000000000"
        ),
        "transactionHash": HexBytes(
            "0x535765c7fe1ca8941958355575275943211183e3a6ae95b508f2334d175d7caf"
        ),
        "transactionIndex": 0,
        "blockHash": HexBytes(
            "0xa332329dd84b99feb00bc83618699269bfdbaa706070f80c84a4a8d8f54afd9a"
        ),
        "blockNumber": 57684584,
        "gasUsed": 144955,
        "effectiveGasPrice": 100000000,
        "blobGasPrice": 1,
        "from": "0xb404993a0129379D1D90e5A52d06652FFD0AE7c3",
        "to": "0x653b40AB9Dd1d1b42845f67F2bE617B2445b7eA5",
        "contractAddress": None,
    }


# 15 CAKE -> 0.048764356437444905 BNB
@fixture
def receipt_cake_bnb() -> dict[str, Any]:
    return {
        "type": 0,
        "status": 1,
        "cumulativeGasUsed": 1150347,
        "logs": [
            {
                "address": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000b404993a0129379d1d90e5a52d06652ffd0ae7c3"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x000000000000000000000000000000000000000000000000d02ab486cedc0000"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 0,
                "removed": False,
            },
            {
                "address": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
                "topics": [
                    HexBytes(
                        "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
                    ),
                    HexBytes(
                        "0x000000000000000000000000b404993a0129379d1d90e5a52d06652ffd0ae7c3"
                    ),
                    HexBytes(
                        "0x000000000000000000000000000000000022d473030f116ddee9f6b43ac78ba3"
                    ),
                ],
                "data": HexBytes(
                    "0xffffffffffffffffffffffffffffffffffffffffffffffff2fd54b793123ffff"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 1,
                "removed": False,
            },
            {
                "address": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x0000000000000000000000003f23b4f1a35794306ba4f3176934012dc73312d1"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000000f97794c2526c000"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 2,
                "removed": False,
            },
            {
                "address": "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x0000000000000000000000003f23b4f1a35794306ba4f3176934012dc73312d1"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x00000000000000000000000000000000000000000000000000025c15f33e0201"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 3,
                "removed": False,
            },
            {
                "address": "0x3f23B4F1a35794306ba4f3176934012dC73312D1",
                "topics": [
                    HexBytes(
                        "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1"
                    )
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000663698d84a188724cd0000000000000000000000000000000000000000000000000f7fb7c80f8d88be"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 4,
                "removed": False,
            },
            {
                "address": "0x3f23B4F1a35794306ba4f3176934012dC73312D1",
                "topics": [
                    HexBytes(
                        "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000000f97794c2526c0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000025c15f33e0201"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 5,
                "removed": False,
            },
            {
                "address": "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000517f28453b947ba01fe6a6b193294d4576528826"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000000005827066135c94"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 6,
                "removed": False,
            },
            {
                "address": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000517f28453b947ba01fe6a6b193294d4576528826"
                    ),
                ],
                "data": HexBytes(
                    "0x00000000000000000000000000000000000000000000000024609ff332561400"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 7,
                "removed": False,
            },
            {
                "address": "0x517F28453B947bA01fE6a6B193294D4576528826",
                "topics": [
                    HexBytes(
                        "0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x00000000000000000000000000000000000000000000000024609ff332561400fffffffffffffffffffffffffffffffffffffffffffffffffffa7d8f99eca36c0000000000000000000000000000000000000000063baf7a63c54ef4d858462c000000000000000000000000000000000000000000000007b3d830a3e83d1f2efffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeddba00000000000000000000000000000000000000000000000000077339be4caa000000000000000000000000000000000000000000000000000000000000000000"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 8,
                "removed": False,
            },
            {
                "address": "0x28e2Ea090877bF75740558f6BFB36A5ffeE9e9dF",
                "topics": [
                    HexBytes(
                        "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
                    ),
                    HexBytes(
                        "0xfe5c9b909829936c85b0ffce50c6faf04b73b614d28a83fcc0bcba209b3a9b38"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0xffffffffffffffffffffffffffffffffffffffffffffffffe5fe3ae1cbff2140000000000000000000000000000000000000000000000000479649af7a0e57f80000000000000000000000000000000000000001a8ac473e5267d4f5b7de9e840000000000000000000000000000000000000000000001c9e2b067456047d5f8000000000000000000000000000000000000000000000000000000000000278b0000000000000000000000000000000000000000000000000000000000000064"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 9,
                "removed": False,
            },
            {
                "address": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x00000000000000000000000028e2ea090877bf75740558f6bfb36a5ffee9e9df"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x000000000000000000000000000000000000000000000000479649af7a0e57f8"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 10,
                "removed": False,
            },
            {
                "address": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x00000000000000000000000028e2ea090877bf75740558f6bfb36a5ffee9e9df"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000001a01c51e3400dec0"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 11,
                "removed": False,
            },
            {
                "address": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x0000000000000000000000003d94d03eb9ea2d4726886ab8ac9fc0f18355fd13"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000000531d211779a6b2c"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 12,
                "removed": False,
            },
            {
                "address": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x0000000000000000000000003d94d03eb9ea2d4726886ab8ac9fc0f18355fd13"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x000000000000000000000000000000000000000000000000000452a08a1f6450"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 13,
                "removed": False,
            },
            {
                "address": "0x3d94d03eb9ea2D4726886aB8Ac9fc0F18355Fd13",
                "topics": [
                    HexBytes(
                        "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1"
                    )
                ],
                "data": HexBytes(
                    "0x00000000000000000000000000000000000000000000036a5346579c9ecf202f000000000000000000000000000000000000000000000002d905a65f43aadaff"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 14,
                "removed": False,
            },
            {
                "address": "0x3d94d03eb9ea2D4726886aB8Ac9fc0F18355Fd13",
                "topics": [
                    HexBytes(
                        "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000000531d211779a6b2c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000452a08a1f6450"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 15,
                "removed": False,
            },
            {
                "address": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x0000000000000000000000001e213600fa9317feac4ef4087acdf5d0e25d7187"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x00000000000000000000000000000000000000000000000000045729dcc880a3"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 16,
                "removed": False,
            },
            {
                "address": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x0000000000000000000000001e213600fa9317feac4ef4087acdf5d0e25d7187"
                    ),
                ],
                "data": HexBytes(
                    "0x000000000000000000000000000000000000000000000000053328b87d9f4a88"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 17,
                "removed": False,
            },
            {
                "address": "0x1E213600FA9317FEAC4Ef4087acDF5D0e25D7187",
                "topics": [
                    HexBytes(
                        "0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x000000000000000000000000000000000000000000000000053328b87d9f4a88fffffffffffffffffffffffffffffffffffffffffffffffffffba8d623377f5d00000000000000000000000000000000000000000e9dbfdbf403908ce085dabe0000000000000000000000000000000000000000000000031c3d18ac0096e71fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff205000000000000000000000000000000000000000000000000000000b3ee1b976920000000000000000000000000000000000000000000000000000000000000000"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 18,
                "removed": False,
            },
            {
                "address": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000afb2da14056725e3ba3a30dd846b6bbbd7886c56"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000000063fe291833d0d9"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 19,
                "removed": False,
            },
            {
                "address": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000afb2da14056725e3ba3a30dd846b6bbbd7886c56"
                    ),
                ],
                "data": HexBytes(
                    "0x00000000000000000000000000000000000000000000000077cbdb5f4e24978c"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 20,
                "removed": False,
            },
            {
                "address": "0xAfB2Da14056725E3BA3a30dD846B6BBbd7886c56",
                "topics": [
                    HexBytes(
                        "0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x00000000000000000000000000000000000000000000000077cbdb5f4e24978cffffffffffffffffffffffffffffffffffffffffffffffffff9c01d6e7cc2f2700000000000000000000000000000000000000000e9f187635070e96875e5378000000000000000000000000000000000000000000004b9be6e9062cb3a979c2ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff2057000000000000000000000000000000000000000000000000000536aa462cda300000000000000000000000000000000000000000000000000000000000000000"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 21,
                "removed": False,
            },
            {
                "address": "0x55d398326f99059fF775485246999027B3197955",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x0000000000000000000000009f599f3d64a9d99ea21e68127bb6ce99f893da61"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x00000000000000000000000000000000000000000000000071b3848296f749f0"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 22,
                "removed": False,
            },
            {
                "address": "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x0000000000000000000000009f599f3d64a9d99ea21e68127bb6ce99f893da61"
                    ),
                ],
                "data": HexBytes(
                    "0x00000000000000000000000000000000000000000000000000064b6b1b76ec9a"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 23,
                "removed": False,
            },
            {
                "address": "0x9F599F3D64a9D99eA21e68127Bb6CE99f893DA61",
                "topics": [
                    HexBytes(
                        "0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x00000000000000000000000000000000000000000000000000064b6b1b76ec9affffffffffffffffffffffffffffffffffffffffffffffff8e4c7b7d6908b610000000000000000000000000000000000000004400dffa79323379480106995300000000000000000000000000000000000000000000009719861714239c1eb200000000000000000000000000000000000000000000000000000000000149ab0000000000000000000000000000000000000000000000000000000d9cfec61a0000000000000000000000000000000000000000000000000000000000000000"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 24,
                "removed": False,
            },
            {
                "address": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000539e0ebfffd39e54a0f7e5f8fec40ade7933a664"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000000e3ab70b5135874c"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 25,
                "removed": False,
            },
            {
                "address": "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000539e0ebfffd39e54a0f7e5f8fec40ade7933a664"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000000000c9b6e61e907c"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 26,
                "removed": False,
            },
            {
                "address": "0x539e0EBfffd39e54A0f7E5F8FEc40ade7933A664",
                "topics": [
                    HexBytes(
                        "0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000000000c9b6e61e907cfffffffffffffffffffffffffffffffffffffffffffffffff1c548f4aeca78b40000000000000000000000000000000000000044024ceedb8bc38725b9263a0100000000000000000000000000000000000000000000001bd6632711a105201000000000000000000000000000000000000000000000000000000000000149ad00000000000000000000000000000000000000000000000000000008c7532b5a0000000000000000000000000000000000000000000000000000000000000000"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 27,
                "removed": False,
            },
            {
                "address": "0x8d0D000Ee44948FC98c9B98A4FA4921476f08B0d",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000370fbd4cc0c5c99ffc8586aaff24a5134601386b"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000000e38b83a73b9b027"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 28,
                "removed": False,
            },
            {
                "address": "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000370fbd4cc0c5c99ffc8586aaff24a5134601386b"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000000000c96457bbe17f"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 29,
                "removed": False,
            },
            {
                "address": "0x370fbd4cC0C5C99FfC8586aAff24a5134601386B",
                "topics": [
                    HexBytes(
                        "0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000000000c96457bbe17ffffffffffffffffffffffffffffffffffffffffffffffffff1c747c58c464fd900000000000000000000000000000000000000440b650de65d75d406c32949290000000000000000000000000000000000000000000000160e29d8a81fcfd4dd00000000000000000000000000000000000000000000000000000000000149b700000000000000000000000000000000000000000000000000000008c3bb66a10000000000000000000000000000000000000000000000000000000000000000"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 30,
                "removed": False,
            },
            {
                "address": "0x28e2Ea090877bF75740558f6BFB36A5ffeE9e9dF",
                "topics": [
                    HexBytes(
                        "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
                    ),
                    HexBytes(
                        "0x05dd2dc106d75562b323bad5d7c26e5677e81a78e6ce0de1cb72c6f64d610bf3"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000000e3795de555ab2a7fffffffffffffffffffffffffffffffffffffffffffffffff1c747c58c464fd90000000000000000000000000000000000000001000892a0fdd3ad30262da6a80000000000000000000000000000000000000000002cb3d36c4457acc22de8a400000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000032"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 31,
                "removed": False,
            },
            {
                "address": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x00000000000000000000000028e2ea090877bf75740558f6bfb36a5ffee9e9df"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000000e3795de555ab2a7"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 32,
                "removed": False,
            },
            {
                "address": "0x8d0D000Ee44948FC98c9B98A4FA4921476f08B0d",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x00000000000000000000000028e2ea090877bf75740558f6bfb36a5ffee9e9df"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000000e38b83a73b9b027"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 33,
                "removed": False,
            },
            {
                "address": "0x28e2Ea090877bF75740558f6BFB36A5ffeE9e9dF",
                "topics": [
                    HexBytes(
                        "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
                    ),
                    HexBytes(
                        "0xf8c7b3c122f31aec155c6beb0c1c78a5e74208358a840cadfbc6129b59391850"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000001c8ab5c205c18d48ffffffffffffffffffffffffffffffffffffffffffffffffe370bf800ee11074000000000000000000000000000000000000000100142b5bf626e1359ddf6185000000000000000000000000000000000000000001bb0a552402a1ac5bf61c0200000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000006"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 34,
                "removed": False,
            },
            {
                "address": "0x55d398326f99059fF775485246999027B3197955",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x00000000000000000000000028e2ea090877bf75740558f6bfb36a5ffee9e9df"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000001c8ab5c205c18d48"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 35,
                "removed": False,
            },
            {
                "address": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x00000000000000000000000028e2ea090877bf75740558f6bfb36a5ffee9e9df"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000001c8f407ff11eef8c"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 36,
                "removed": False,
            },
            {
                "address": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000f2688fb5b81049dfb7703ada5e770543770612c4"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000000015ad615c3f8769"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 37,
                "removed": False,
            },
            {
                "address": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000f2688fb5b81049dfb7703ada5e770543770612c4"
                    ),
                ],
                "data": HexBytes(
                    "0x000000000000000000000000000000000000000000000000477956192f7fa25f"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 38,
                "removed": False,
            },
            {
                "address": "0xf2688Fb5B81049DFB7703aDa5e770543770612C4",
                "topics": [
                    HexBytes(
                        "0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x000000000000000000000000000000000000000000000000477956192f7fa25fffffffffffffffffffffffffffffffffffffffffffffffffffea529ea3c07897000000000000000000000000000000000000000008cfd931fba6c7005248eccc000000000000000000000000000000000000000000008a4f8f9447f1882ecc59fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffef8c700000000000000000000000000000000000000000000000000009a936e007fe40000000000000000000000000000000000000000000000000000000000000000"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 39,
                "removed": False,
            },
            {
                "address": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x00000000000000000000000047a90a2d92a8367a91efa1906bfc8c1e05bf10c4"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x000000000000000000000000000000000000000000000000002b2ba3143a0b20"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 40,
                "removed": False,
            },
            {
                "address": "0x55d398326f99059fF775485246999027B3197955",
                "topics": [
                    HexBytes(
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x00000000000000000000000047a90a2d92a8367a91efa1906bfc8c1e05bf10c4"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000008e3e3a449cb8d738"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 41,
                "removed": False,
            },
            {
                "address": "0x47a90A2d92A8367A91EfA1906bFc8c1E05bf10c4",
                "topics": [
                    HexBytes(
                        "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x0000000000000000000000000000000000000000000000008e3e3a449cb8d738ffffffffffffffffffffffffffffffffffffffffffffffffffd4d45cebc5f4e0000000000000000000000000000000000000000008d09ffe3240e758b331550e000000000000000000000000000000000000000000022e03d082a90fc0773a53fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffef8ce"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 42,
                "removed": False,
            },
            {
                "address": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                "topics": [
                    HexBytes(
                        "0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65"
                    ),
                    HexBytes(
                        "0x000000000000000000000000653b40ab9dd1d1b42845f67f2be617b2445b7ea5"
                    ),
                ],
                "data": HexBytes(
                    "0x00000000000000000000000000000000000000000000000000ad80f7ef954855"
                ),
                "blockHash": HexBytes(
                    "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
                ),
                "blockNumber": 57684586,
                "blockTimestamp": "0x689f46e4",
                "transactionHash": HexBytes(
                    "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
                ),
                "transactionIndex": 0,
                "logIndex": 43,
                "removed": False,
            },
        ],
        "logsBloom": HexBytes(
            "0x002000000000000000000000800200040000080000000000000000100000000081000000000080800010002000430000000000808400200000800a00202400a00480280002402008810040181000042080000020004408320004000002010000000400000400000100020001040008000000002100000405000000101008000000000000004880008080000000202080010400000001000c2020004000000000020000000000000041000000101000003000000040000000000000010000000000008002000005100000000000000000200000000020001400102002000080100210000004004002804000000200000002002008000000000040000000800000"
        ),
        "transactionHash": HexBytes(
            "0xd2d989ce5a1f43fd6e76778ae8de3e4043b0a8f424f9f624c9c55d6ed84d3f9a"
        ),
        "transactionIndex": 0,
        "blockHash": HexBytes(
            "0x11717bb769802bae5526c12ab83ba2f6ea56d26849cc1ec5874255e14a78a78a"
        ),
        "blockNumber": 57684586,
        "gasUsed": 1150347,
        "effectiveGasPrice": 100000000,
        "blobGasPrice": 1,
        "from": "0xb404993a0129379D1D90e5A52d06652FFD0AE7c3",
        "to": "0x653b40AB9Dd1d1b42845f67F2bE617B2445b7eA5",
        "contractAddress": None,
    }


@fixture
def w3():
    return AsyncWeb3(AsyncHTTPProvider("http://127.0.0.1:8545"))


@mark.asyncio
async def test_bsc_transaction_receipt_parser_sell_native_buy_token(
    w3: AsyncWeb3, receipt_bnb_cake: TxReceipt
):
    parser = BscTransactionReceiptParser(w3=w3)

    result = await parser.parse_receipt(
        receipt=receipt_bnb_cake,
        address="0xb404993a0129379D1D90e5A52d06652FFD0AE7c3",
        sell_token=bnb_token,
        buy_token=cake_token,
    )

    assert result == ParsedReceipt(
        executed_sell_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("0.032491479685227543"),
            amount_atomic=32491479685227543,
            decimals=18,
        ),
        executed_buy_balance=BalanceAtomic(
            asset=cake_token,
            amount=Decimal("9.955195991456078905"),
            amount_atomic=9955195991456078905,
            decimals=18,
        ),
        rate=Decimal("306.3940481597171398289795518"),
    )

    print(f"result: {result}")


@mark.asyncio
async def test_bsc_transaction_receipt_parser_sell_token_buy_native(
    w3: AsyncWeb3, receipt_cake_bnb: TxReceipt
):
    parser = BscTransactionReceiptParser(w3=w3)

    result = await parser.parse_receipt(
        receipt=receipt_cake_bnb,
        address="0xb404993a0129379D1D90e5A52d06652FFD0AE7c3",
        sell_token=cake_token,
        buy_token=bnb_token,
    )

    assert result == ParsedReceipt(
        executed_sell_balance=BalanceAtomic(
            asset=cake_token,
            amount=Decimal("15"),
            amount_atomic=15000000000000000000,
            decimals=18,
        ),
        executed_buy_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("0.048836973335758933"),
            amount_atomic=48836973335758933,
            decimals=18,
        ),
        rate=Decimal("0.003255798222383928866666666667"),
    )
