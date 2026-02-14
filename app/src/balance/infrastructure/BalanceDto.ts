import type { Balance } from '../Balance'
import type { BalanceResponse } from './BalanceAtomicDto'
import Big from 'big.js'
import { AssetDto } from '@/asset/infrastructure/AssetDto'

export class BalanceDto {
  static toRequest(balance: Balance) {
    return {
      asset: AssetDto.toRequest(balance.asset),
      amount: balance.amount.toFixed(),
    }
  }

  static fromResponse(balanceResponse: BalanceResponse): Balance {
    return {
      asset: AssetDto.fromResponse(balanceResponse.asset),
      amount: Big(balanceResponse.amount),
    }
  }
}
