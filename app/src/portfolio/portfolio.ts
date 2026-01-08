import type { Asset } from '@/asset/Asset'
import type { Balance } from '@/balance/Balance'
import type { BalanceAtomic } from '@/balance/BalanceAtomic'

export interface ConvertedBalance {
  sellBalance: Balance
  buyBalance: Balance
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
