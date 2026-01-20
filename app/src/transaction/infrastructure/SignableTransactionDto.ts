import type { SignableTransaction } from '../signable-transaction'
import z from 'zod'

const AmountSchema = z.string().regex(/^\d+$/, {
  message: 'Must be an integer string',
})

export const SignableTransactionResponseSchema = z.object({
  type: z.union([z.literal('SIGN'), z.literal('SEND')]),
  amount: AmountSchema,
  data: z.string(),
  gas: z
    .object({
      gas: AmountSchema.optional(),
      gas_price: AmountSchema.optional(),
    })
    .optional(),
  to_address: z.string().optional(),
})

type SignableTransactionResponse = z.infer<typeof SignableTransactionResponseSchema>

export class SignableTransactionDto {
  static fromResponse(
    signableTransactionResponse: SignableTransactionResponse,
  ): SignableTransaction {
    return {
      type: signableTransactionResponse.type,
      amount: BigInt(signableTransactionResponse.amount),
      data: signableTransactionResponse.data,
      gas: signableTransactionResponse.gas
        ? {
            gas: signableTransactionResponse.gas.gas
              ? BigInt(signableTransactionResponse.gas.gas)
              : undefined,
            gas_price: signableTransactionResponse.gas.gas_price
              ? BigInt(signableTransactionResponse.gas.gas_price)
              : undefined,
          }
        : undefined,
      toAddress: signableTransactionResponse.to_address,
    }
  }
}
