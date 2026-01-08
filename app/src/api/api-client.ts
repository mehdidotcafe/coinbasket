import type { Portfolio } from '../portfolio/portfolio'
import type { Token } from '@/asset/Token'
import type { ConfirmedOrder } from '@/invest/order/confirmed-order'
import type { SignableOrder } from '@/invest/order/signable-order'

export interface ApiClient {
  getPortfolio: (token: Token) => Promise<Portfolio>
  getSignableOrder: (confirmedOrder: ConfirmedOrder) => Promise<SignableOrder>
}
