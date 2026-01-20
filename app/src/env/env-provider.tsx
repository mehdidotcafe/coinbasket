import type { Env, NotValidatedEnv } from './env'
import React, { createContext } from 'react'
import { validateEnv } from './env'

export const EnvContext = createContext<Env | null>(null)

export const EnvProvider: React.FC<{ children: React.ReactNode, env: NotValidatedEnv }> = ({
  children,
  env,
}) => {
  const value = validateEnv(env)
  return <EnvContext.Provider value={value}>{children}</EnvContext.Provider>
}
