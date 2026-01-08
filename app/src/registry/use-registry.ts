'use client'

import type { Registry } from './Registry'
import { createContext, useContext } from 'react'

export const RegistryContext = createContext<Registry | null>(null)

export function useRegistry(): Registry {
  const context = useContext(RegistryContext)

  if (!context) {
    throw new Error('useRegistry must be used within a RegistryProvider')
  }
  return context
}
