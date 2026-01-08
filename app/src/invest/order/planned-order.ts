import type { Asset } from '@/asset/Asset'

interface PlannedOrderBalance {
  asset: Asset
  availableAmount: Big
  amount?: Big
}

export interface PlannedOrder {
  id: string
  sellAssetWithAmount: PlannedOrderBalance
  buyAssetWithAmount: PlannedOrderBalance
}
