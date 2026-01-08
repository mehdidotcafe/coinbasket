interface QueryMessageContentSignedOrder {
  status: 'CONFIRM' | 'CANCEL'
  signableOrderId?: string
  transactionHash?: string
}

export interface QueryMessage {
  id: string
  role: 'user'
  isResuming: boolean
  content: string | QueryMessageContentSignedOrder
  createdAt?: Date
}
