import type { Asset } from '@/asset/Asset'

export interface MessageUiConfirmPlannedOrder {
  id: 'confirm_planned_order'
  args: {
    plannedOrder: {
        id: string
        buyAssetWithAmount: {
          asset: Asset
          availableAmount: Big
          amount?: Big
        }
        sellAssetWithAmount: {
          asset: Asset
          availableAmount: Big
          amount?: Big
        }
    }
  }
}

export type MessageUi = MessageUiConfirmPlannedOrder
