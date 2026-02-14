import type { Asset } from '@/asset/Asset'
import type { Balance } from '@/balance/Balance'
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

export interface MessageUiAssetPriceCard {
  id: 'asset_price_card'
  args: {
    sellBalance: Balance
    buyBalance: Balance
  }
}

export type MessageUi = MessageUiConfirmPlannedOrder | MessageUiAssetPriceCard
