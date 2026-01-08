import { useContext } from 'react'
import { AuthenticationContext } from './authentication-provider'

export function useAuthentication() {
  const context = useContext(AuthenticationContext)
  if (context === null) {
    throw new Error('useAuthentication must be used within an AuthenticationProvider')
  }
  return context
}
