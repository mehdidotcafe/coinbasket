import type { Balance } from '@/balance/Balance'

export interface ConfirmedOrder {
  plannedOrderId: string
  sellBalance: Balance
  buyBalance: Balance
}
