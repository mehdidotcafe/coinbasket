import type { Credential } from '@/authentication/credential'
import type { Address } from '@/chain/address'

export type Authentication = {
  authStatus: 'unauthenticated'
} | {
  authStatus: 'authenticated'
  credential: Credential
  address: Address
}
