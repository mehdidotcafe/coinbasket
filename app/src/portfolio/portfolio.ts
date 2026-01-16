import type { Asset } from '@/asset/Asset'
import type { Balance } from '@/balance/Balance'
import type { BalanceAtomic } from '@/balance/BalanceAtomic'
import type { Fees } from '@/fee/fees'

export interface ConvertedBalance {
    sellBalance: Balance
    buyBalance: Balance
    fees: Fees
}

interface PortfolioBalance {
    nativeBalance: BalanceAtomic<Asset>
    convertedBalance: BalanceAtomic<Asset>
}

export interface Portfolio {
    availableBalance: PortfolioBalance
    holdingBalances: PortfolioBalance[]
    totalBalance: BalanceAtomic
}
