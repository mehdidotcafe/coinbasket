import type { Asset } from '@/asset/Asset'

export interface BalanceAtomic<T extends Asset = Asset> {
  asset: T
  amount: Big
  amountAtomic: bigint
}
