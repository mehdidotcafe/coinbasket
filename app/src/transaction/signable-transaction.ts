export interface SignableTransaction {
  type: 'SIGN' | 'SEND'
  amount: bigint
  data: string
  gas?: Gas
  toAddress?: string
}

interface Gas {
    gas?: bigint
    gas_price?: bigint
}
