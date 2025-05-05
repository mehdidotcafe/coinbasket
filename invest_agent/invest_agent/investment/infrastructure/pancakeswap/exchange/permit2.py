import json
from eth_typing import HexStr, ChecksumAddress
from eth_account.signers.local import LocalAccount
from uniswap_universal_router_decoder import RouterCodec
from web3 import Web3
from web3.types import TxReceipt, TxParams, Wei

from invest_agent.chain.chain import Chain


# https://github.com/Uniswap/permit2/blob/main/src/interfaces/IAllowanceTransfer.sol
# https://github.com/Elnaril/uniswap-universal-router-decoder
class Permit2:
    def __init__(
        self,
        chain: Chain,
        permit2_contract_address: str,
        bsc_rpc_url: str,
        private_key: str,
    ):
        self.chain = chain
        self.permit2_contract_address = Web3.to_checksum_address(
            permit2_contract_address
        )
        self.bsc_rpc_url = bsc_rpc_url
        self.w3 = Web3(Web3.HTTPProvider(bsc_rpc_url))

        self.account: LocalAccount = self.w3.eth.account.from_key(private_key)
        self.codec = RouterCodec()

        with open(
            "./invest_agent/investment/infrastructure/pancakeswap/exchange/permit2_contract_abi.json",
            "r",
        ) as f:
            self.permit2_contract_abi = json.load(f)

        with open(
            "./invest_agent/infrastructure/bsc/chain/erc20_token_abi.json",
            "r",
        ) as f:
            self.erc20_token_abi = json.load(f)

    def approve_permit2_contract(
        self,
        token_address: ChecksumAddress,
    ) -> TxReceipt:
        amount = Wei(0)
        permit2_allowance = 2**256 - 1

        token_contract = self.w3.eth.contract(
            address=token_address,
            abi=self.erc20_token_abi,
        )

        contract_function = token_contract.functions.approve(
            self.permit2_contract_address,
            permit2_allowance,
        )
        encoded_input = contract_function._encode_transaction_data()

        try:
            gas_estimate = self.chain.compute_gas_estimate(
                amount,
                token_address,
                encoded_input,
            )
        except Exception as e:
            print(f"Error estimating gas: {e}")
            raise e

        transaction_params: TxParams = {
            "from": self.account.address,
            "gas": gas_estimate,
            "maxPriorityFeePerGas": self.w3.eth.max_priority_fee,
            "maxFeePerGas": Wei(100 * 10**9),
            "type": HexStr("0x2"),
            "chainId": self.w3.eth.chain_id,
            "value": amount,
            "nonce": self.w3.eth.get_transaction_count(self.account.address, "pending"),
        }
        transaction = contract_function.build_transaction(transaction_params)
        raw_transaction = self.w3.eth.account.sign_transaction(
            transaction, self.account.key
        ).raw_transaction
        transaction_hash = self.w3.eth.send_raw_transaction(raw_transaction)
        print(f"Permit2 Trx Hash: {transaction_hash.hex()}")

        receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash)
        print(f"Permit2 Receipt: {receipt}")

        return receipt

    def sign_permit2_message(
        self, token_address: ChecksumAddress, spender: ChecksumAddress
    ):
        allowance_amount = Wei(2**160 - 1)  # max/infinite
        deadline = self.codec.get_default_deadline()  # 180 seconds
        permit2_nonce = self.get_permit2_nonce(token_address, spender)

        permit_data, signable_message = self.codec.create_permit2_signable_message(
            token_address=token_address,
            amount=allowance_amount,
            expiration=self.codec.get_default_expiration(),  # 30 days
            nonce=permit2_nonce,
            spender=spender,
            deadline=deadline,
            chain_id=self.w3.eth.chain_id,
            verifying_contract=self.permit2_contract_address,
        )
        signed_message = self.account.sign_message(signable_message)

        return signed_message, permit_data, deadline

    def get_permit2_nonce(
        self, token_address: ChecksumAddress, spender: ChecksumAddress
    ) -> int:
        _permit2_amount, _permit2_expiration, permit2_nonce = (
            self.codec.fetch_permit2_allowance(
                wallet=self.account.address,
                token=token_address,
                spender=spender,
                permit2=self.permit2_contract_address,
                permit2_abi=self.permit2_contract_abi,
            )
        )

        return permit2_nonce

    def get_default_deadline(self) -> int:
        return self.codec.get_default_deadline()
