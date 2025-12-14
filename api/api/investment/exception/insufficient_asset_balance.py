from protocol.asset import Asset


class InsufficientAssetBalance(Exception):
    """
    Exception raised when attempting to sell an asset without sufficient balance
    """

    def __init__(self, asset: Asset):
        super().__init__(f"Insufficient balance for asset: {asset}")
