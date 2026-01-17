import type { AssetSwapPriceInfo } from './client/pricer-client'
import type { ConvertedBalance } from '@/portfolio/portfolio'
import { useMutation } from '@tanstack/react-query'
import Big from 'big.js'
import { useRegistry } from '../registry/use-registry'

export function usePricer() {
  const { pricerClient } = useRegistry()

  const getPrice = useMutation({
    mutationFn: async (priceInfo: AssetSwapPriceInfo): Promise<ConvertedBalance> => {
      if (priceInfo.sellAssetAmount.eq(Big(0))) {
        return {
          sellBalance: {
            asset: priceInfo.sellAsset,
            amount: Big(0),
          },
          buyBalance: {
            asset: priceInfo.buyAsset,
            amount: Big(0),
          },
          fees: {
            platformFee: undefined,
            providerFee: undefined,
            gasFee: undefined,
          },
        }
      }

      const { sellBalance, buyBalance, fees } = await pricerClient.getPrice({
        buyAsset: priceInfo.buyAsset,
        sellAsset: priceInfo.sellAsset,
        sellAssetAmount: priceInfo.sellAssetAmount,
      })

      return {
        sellBalance,
        buyBalance,
        fees,
      }
    },
  })

  return {
    getPrice: getPrice.mutateAsync,
  }
}
