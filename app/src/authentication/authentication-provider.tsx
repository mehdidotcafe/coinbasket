import type { Authentication } from './authentication'
import type { Credential } from '@/authentication/credential'
import type { Address } from '@/chain/address'
import { createAuthenticationAdapter, RainbowKitAuthenticationProvider } from '@rainbow-me/rainbowkit'
import React, { createContext, useState } from 'react'
import { createSiweMessage } from 'viem/siwe'
import { useRegistry } from '@/registry/use-registry'

export const AuthenticationContext = createContext<Authentication>({
  authStatus: 'unauthenticated',
})

function extractAddressFromCredential(credential: Credential): Address | undefined {
  try {
    const payload = credential.split('.')[1]
    const decoded = JSON.parse(atob(payload))
    return decoded.address as Address
  }
  catch {
    return undefined
  }
}

export const AuthenticationProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { siweClient } = useRegistry()

  const [auth, setAuth] = useState<Authentication>({ authStatus: 'unauthenticated' })

  const authenticationAdapter = createAuthenticationAdapter({
    getNonce: siweClient.getNonce,

    createMessage: ({ nonce, address, chainId }) => {
      return createSiweMessage({
        domain: window.location.host,
        scheme: 'http',
        address,
        statement: 'Sign in with Ethereum to the app.',
        uri: window.location.origin,
        version: '1',
        chainId,
        nonce,
      })
    },

    verify: async (messageAndSignature) => {
      try {
        const credential: Credential = await siweClient.verifySignature(messageAndSignature)

        const address = extractAddressFromCredential(credential)

        if (!address) {
          console.error('Failed to extract address from credential')
          setAuth({ authStatus: 'unauthenticated' })
          return false
        }

        setAuth({ authStatus: 'authenticated', credential, address })
        return true
      }
      catch { }
      setAuth({ authStatus: 'unauthenticated' })
      return false
    },

    signOut: async () => {
      await siweClient.signOut()
      setAuth({ authStatus: 'unauthenticated' })
    },
  })

  return (
    <AuthenticationContext.Provider value={auth}>
      <RainbowKitAuthenticationProvider
        adapter={authenticationAdapter}
        status={auth.authStatus}
      >
        {children}
      </RainbowKitAuthenticationProvider>
    </AuthenticationContext.Provider>
  )
}
