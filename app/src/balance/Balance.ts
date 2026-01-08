import type { Asset } from '@/asset/Asset'

export interface Balance {
  asset: Asset
  amount: Big
}
