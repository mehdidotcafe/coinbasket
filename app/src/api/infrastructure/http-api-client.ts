import type { ApiClient } from '../api-client'
import type { ConfirmedOrder } from '@/invest/order/confirmed-order'
import type { Portfolio } from '@/portfolio/portfolio'
import Big from 'big.js'
import urlJoin from 'url-join'
import * as z from 'zod'
import { AssetDto } from '@/asset/infrastructure/AssetDto'
import { TokenDto } from '@/asset/infrastructure/TokenDto'
import { BalanceAtomicDto, BalanceAtomicSchema } from '@/balance/infrastructure/BalanceAtomicDto'
import { BalanceDto } from '@/balance/infrastructure/BalanceDto'
import { SignableTransactionDto, SignableTransactionResponseSchema } from '@/transaction/infrastructure/SignableTransactionDto'

const defaultHeaders = {
  'Content-Type': 'application/json',
  'accept': 'application/json',
}

const PortfolioBalanceSchema = z.object({
  native_balance: BalanceAtomicSchema,
  converted_balance: BalanceAtomicSchema,
})

const PortfolioResponseSchema = z.object({
  available_balance: PortfolioBalanceSchema,
  holding_balances: z.array(PortfolioBalanceSchema),
  total_balance: BalanceAtomicSchema,
})

type PortfolioResponse = z.infer<typeof PortfolioResponseSchema>

class PortfolioDto {
  static fromResponse(portfolioResponse: PortfolioResponse): Portfolio {
    return {
      availableBalance: {
        nativeBalance: BalanceAtomicDto.fromResponse(portfolioResponse.available_balance.native_balance),
        convertedBalance: BalanceAtomicDto.fromResponse(portfolioResponse.available_balance.converted_balance),
      },
      holdingBalances: portfolioResponse.holding_balances.map(holdingBalance => ({
        nativeBalance: BalanceAtomicDto.fromResponse(holdingBalance.native_balance),
        convertedBalance: BalanceAtomicDto.fromResponse(holdingBalance.converted_balance),
      })),
      totalBalance: {
        asset: AssetDto.fromResponse(portfolioResponse.total_balance.asset),
        amount: Big(portfolioResponse.total_balance.amount),
        amountAtomic: BigInt(portfolioResponse.total_balance.amount_atomic),
      },
    }
  }
}

class ConfirmedOrderDto {
  static toRequest(confirmedOrder: ConfirmedOrder) {
    return {
      planned_order_id: confirmedOrder.plannedOrderId,
      sell_balance: BalanceDto.toRequest(confirmedOrder.sellBalance),
      buy_balance: BalanceDto.toRequest(confirmedOrder.buyBalance),
    }
  }
}

const SignableOrderResponseSchema = z.object({
  id: z.string(),
  buy_balance: BalanceAtomicSchema,
  sell_balance: BalanceAtomicSchema,
  signature_payload: z.record(z.string(), z.any()).optional().nullable(),
  transaction: SignableTransactionResponseSchema,
})

type SignableOrderResponse = z.infer<typeof SignableOrderResponseSchema>

class SignableOrderDto {
  static fromResponse(signableOrderResponse: SignableOrderResponse) {
    return {
      id: signableOrderResponse.id,
      buyBalance: BalanceAtomicDto.fromResponse(signableOrderResponse.buy_balance),
      sellBalance: BalanceAtomicDto.fromResponse(signableOrderResponse.sell_balance),
      signaturePayload: signableOrderResponse.signature_payload || undefined,
      transaction: SignableTransactionDto.fromResponse(signableOrderResponse.transaction),
    }
  }
}

export function httpApiClient(baseUrl: string): ApiClient {
  return {
    getPortfolio: async (token) => {
      return fetch(urlJoin(baseUrl, 'portfolio'), {
        method: 'POST',
        credentials: 'include',
        headers: defaultHeaders,
        body: JSON.stringify({
          token: TokenDto.toRequest(token),
        }),
      }).then((response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok')
        }

        return response.json()
      }).then((maybePortfolioResponse) => {
        return PortfolioResponseSchema.parseAsync(maybePortfolioResponse)
      }).then((data: PortfolioResponse) => {
        return PortfolioDto.fromResponse(data)
      }).catch((error) => {
        console.error('Error fetching portfolio:', error)
        throw error
      })
    },

    getSignableOrder: async (confirmedOrder) => {
      return fetch(urlJoin(baseUrl, 'order', 'signable'), {
        method: 'POST',
        credentials: 'include',
        headers: defaultHeaders,
        body: JSON.stringify(ConfirmedOrderDto.toRequest(confirmedOrder)),
      }).then((response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok')
        }

        return response.json()
      }).then((maybeSignableOrderResponse) => {
        return SignableOrderResponseSchema.parseAsync(maybeSignableOrderResponse)
      }).then((data: SignableOrderResponse) => {
        return SignableOrderDto.fromResponse(data)
      }).catch((error) => {
        console.error('Error fetching portfolio:', error)
        throw error
      })
    },
  }
}
