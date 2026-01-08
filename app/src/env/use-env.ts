import type { Env } from './env'
import { useContext } from 'react'
import { EnvContext } from './env-provider'

export function useEnv(): Env {
  const env = useContext(EnvContext)
  if (!env) {
    throw new Error('useEnv must be used within an <EnvProvider>')
  }
  return env
}
