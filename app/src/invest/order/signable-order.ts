import type { BalanceAtomic } from '@/balance/BalanceAtomic'
import type { SignableTransaction } from '@/transaction/signable-transaction'

type SignaturePayload = Record<string, unknown>

export interface ApprovalTransaction {
  tokenAddress: string
  spenderAddress: string
  data: string
  amount: string
}

export interface SignableOrder {
  id: string
  buyBalance: BalanceAtomic
  sellBalance: BalanceAtomic
  signaturePayload?: SignaturePayload
  transaction: SignableTransaction
  approvalTransaction?: ApprovalTransaction
}
