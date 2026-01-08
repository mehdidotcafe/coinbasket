export interface Token {
  name: string
  displayName: string
  ticker: string
  id: string
  address: string
  categories: string[]
  decimals: number
  description: string
  type: 'TOKEN'
  logoUri?: string
}
