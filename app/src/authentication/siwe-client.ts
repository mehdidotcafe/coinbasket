import type { Credential } from './credential'

export interface SiweClient {
  getNonce: () => Promise<string>
  verifySignature: ({
    message,
    signature,
  }: {
    message: string
    signature: string
  }) => Promise<Credential>
  signOut: () => Promise<boolean>
}
