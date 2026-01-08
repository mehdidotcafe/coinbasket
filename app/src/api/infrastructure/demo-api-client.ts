import type { ApiClient } from '../api-client'
import Big from 'big.js'
import data from './demo-data'

export const demoApiClient: ApiClient = {
  getPortfolio: async (_token) => {
    const randomValue = Math.floor(Math.random() * 5) - 2

    return {
      ...data[0].portfolio,
      totalBalance: {
        ...data[0].portfolio.totalBalance,
        amount: Big(data[0].portfolio.totalBalance.amount).plus(Big(data[0].portfolio.totalBalance.amount).times(randomValue).div(100)),
        amountAtomic: BigInt(data[0].portfolio.totalBalance.amountAtomic) + BigInt(randomValue * 10 ** 18),
      },
    }
  },

  getSignableOrder: async (confirmedOrder) => {
    const getDecimals = (asset: any) => ('decimals' in asset ? asset.decimals : 18)

    const buyAmountAtomic = BigInt(Math.floor(confirmedOrder.buyBalance.amount.toNumber() * 10 ** getDecimals(confirmedOrder.buyBalance.asset)))
    const sellAmountAtomic = BigInt(Math.floor(confirmedOrder.sellBalance.amount.toNumber() * 10 ** getDecimals(confirmedOrder.sellBalance.asset)))

    return {
      id: `signable-order-${Math.random().toString(36).substring(2, 15)}`,
      buyBalance: {
        asset: confirmedOrder.buyBalance.asset,
        amount: confirmedOrder.buyBalance.amount,
        amountAtomic: buyAmountAtomic,
      },
      sellBalance: {
        asset: confirmedOrder.sellBalance.asset,
        amount: confirmedOrder.sellBalance.amount,
        amountAtomic: sellAmountAtomic,
      },
      transaction: {
        type: 'SIGN' as const,
        amount: sellAmountAtomic,
        data: `0x${Math.random().toString(16).substring(2, 10)}`,
        toAddress: '0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c',
      },
    }
  },
}
