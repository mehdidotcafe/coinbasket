class SwapInsufficientLiquidity(Exception):
    def __init__(self):
        self.message = "Insufficient liquidity for the swap."
        super().__init__(self.message)
