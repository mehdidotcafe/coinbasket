import type { Balance } from '../Balance'
import { AssetDto } from '@/asset/infrastructure/AssetDto'

export class BalanceDto {
  static toRequest(balance: Balance) {
    return {
      asset: AssetDto.toRequest(balance.asset),
      amount: balance.amount.toString(),
    }
  }
}
