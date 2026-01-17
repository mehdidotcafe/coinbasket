import type { Asset } from '@/asset/Asset'
import type { Fees } from '@/fee/fees'

interface AssetWithAmount {
  asset: Asset
  availableAmount: Big
  amount?: Big
}

export interface MessageUiConfirmPlannedOrder {
  id: 'confirm_planned_order'
  args: {
    plannedOrder: {
      id: string
      buyAssetWithAmount: AssetWithAmount
      sellAssetWithAmount: AssetWithAmount
      fees: Fees
    }
  }
}

export type MessageUi = MessageUiConfirmPlannedOrder
