import type { PricerClient } from '../pricer-client'
import Big from 'big.js'

export const demoPricerClient: PricerClient = {
  getPrice: async ({ buyAsset, sellAsset, sellAssetAmount }) => {
    const randomBuyAssetAmount = Big(Math.floor(Math.random() * 1000))

    return {
      sellBalance: {
        asset: sellAsset,
        amount: sellAssetAmount,
      },
      buyBalance: {
        asset: buyAsset,
        amount: randomBuyAssetAmount,
      },
      fees: {
        platformFee: undefined,
        providerFee: undefined,
        gasFee: undefined,
      },
    }
  },
}
