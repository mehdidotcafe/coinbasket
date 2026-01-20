import type { BalanceAtomic } from '@/balance/BalanceAtomic'

export interface Fees {
  gasFee?: BalanceAtomic
  providerFee?: BalanceAtomic
  platformFee?: BalanceAtomic
}
