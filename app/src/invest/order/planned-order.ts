import type { Asset } from '@/asset/Asset'
import type { Fees } from '@/fee/fees'

interface PlannedOrderBalance {
  asset: Asset
  availableAmount: Big
  amount?: Big
}

export interface PlannedOrder {
  id: string
  sellAssetWithAmount: PlannedOrderBalance
  buyAssetWithAmount: PlannedOrderBalance
  fees?: Fees
}
