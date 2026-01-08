import type { BalanceAtomic } from '../BalanceAtomic'
import Big from 'big.js'
import * as z from 'zod'
import { AssetDto, AssetResponseSchema } from '@/asset/infrastructure/AssetDto'

export const BalanceAtomicSchema = z.object({
  asset: AssetResponseSchema,
  amount: z.string(),
  amount_atomic: z.string().regex(/^-?\d+$/, {
    message: 'Must be an integer string',
  }),
})

type BalanceAtomicResponse = z.infer<typeof BalanceAtomicSchema>

export class BalanceAtomicDto {
  static fromResponse(balanceResponse: BalanceAtomicResponse): BalanceAtomic {
    return {
      asset: AssetDto.fromResponse(balanceResponse.asset),
      amount: Big(balanceResponse.amount),
      amountAtomic: BigInt(balanceResponse.amount_atomic),
    }
  }

  static toRequest(balance: BalanceAtomic) {
    return {
      asset: AssetDto.toRequest(balance.asset),
      amount: balance.amount.toString(),
    }
  }
}
