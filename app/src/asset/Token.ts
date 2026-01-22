export interface Token {
  name: string
  displayName: string
  ticker: string
  id: string
  address: string
  categories: string[]
  decimals: number
  description: string
  trustScore: number
  type: 'TOKEN'
  logoUri?: string
}
