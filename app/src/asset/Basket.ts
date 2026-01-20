export interface Basket {
  name: string
  displayName: string
  ticker: string
  id: string
  address: string
  categories: string[]
  decimals: number
  description: string
  type: 'BASKET'
  logoUri?: string
}
