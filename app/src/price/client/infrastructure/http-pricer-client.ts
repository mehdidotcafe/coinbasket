import type { PricerClient } from '../pricer-client'
import Big from 'big.js'
import urlJoin from 'url-join'
import * as z from 'zod'
import { AssetDto, AssetResponseSchema } from '@/asset/infrastructure/AssetDto'

const defaultHeaders = {
  'Content-Type': 'application/json',
  'accept': 'application/json',
}

const BalanceResponseSchema = z.object({
  amount: z.string(),
  asset: AssetResponseSchema,
})

const ConvertedBalanceResponseSchema = z.object({
  sell_balance: BalanceResponseSchema,
  buy_balance: BalanceResponseSchema,
})

export function httpPricerClient(baseUrl: string): PricerClient {
  return {
    getPrice: async (priceInfo) => {
      return fetch(urlJoin(baseUrl, 'asset', 'swap', 'price'), {
        method: 'POST',
        credentials: 'include',
        headers: {
          ...defaultHeaders,
        },
        body: JSON.stringify({
          buy_asset: AssetDto.toRequest(priceInfo.buyAsset),
          sell_asset: AssetDto.toRequest(priceInfo.sellAsset),
          sell_asset_amount: priceInfo.sellAssetAmount.toFixed(),
        }),
      }).then((res) => {
        if (!res.ok) {
          throw new Error(`Network response was not ok: ${res.status}`)
        }

        return res.json()
      }).then((maybeConvertedBalanceResponse) => {
        return ConvertedBalanceResponseSchema.parseAsync(maybeConvertedBalanceResponse)
      }).then((convertedBalanceResponse) => {
        return {
          sellBalance: {
            asset: AssetDto.fromResponse(convertedBalanceResponse.sell_balance.asset),
            amount: Big(convertedBalanceResponse.sell_balance.amount),
          },
          buyBalance: {
            asset: AssetDto.fromResponse(convertedBalanceResponse.buy_balance.asset),
            amount: Big(convertedBalanceResponse.buy_balance.amount),
          },
        }
      })
    },
  }
}
