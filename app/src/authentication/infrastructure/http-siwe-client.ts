import type { Credential } from '../credential'
import type { SiweClient } from '../siwe-client'
import urlJoin from 'url-join'
import z from 'zod'

const NonceResponseSchema = z.object({
  nonce: z.string(),
})

const VerifySignatureResponseSchema = z.object({
  credential: z.string(),
})

export function httpSiweClient(baseUrl: string): SiweClient {
  return {
    getNonce: async () => {
      const data = await fetch(urlJoin(baseUrl, 'auth', 'nonce'), {
        method: 'GET',
        credentials: 'include',
      }).then(async (response) => {
        const data = await response.json()

        if (!response.ok) {
          throw new Error(`Network response was not ok: ${data}`)
        }

        return data
      }).then((maybeNonceResponse) => {
        return NonceResponseSchema.parseAsync(maybeNonceResponse)
      })

      return data.nonce
    },

    verifySignature: async ({ message, signature }) => {
      const data = await fetch(urlJoin(baseUrl, 'auth', 'verify'), {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, signature }),
      }).then(async (response) => {
        const data = await response.json()

        if (!response.ok) {
          throw new Error(`Network response was not ok: ${data}`)
        }

        return data
      }).then((maybeVerifySignatureResponse) => {
        return VerifySignatureResponseSchema.parseAsync(maybeVerifySignatureResponse)
      })

      return data.credential as Credential
    },

    signOut: async () => {
      const response = await fetch(urlJoin(baseUrl, 'auth', 'signout'), {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
      })

      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.statusText}`)
      }

      return true
    },
  }
}
