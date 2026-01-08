import type { Registry } from './Registry'
import { RegistryContext } from './use-registry'

interface Props {
  registry: Registry
  children: React.ReactNode
}

export function RegistryProvider({ registry, children }: Props) {
  return (
    <RegistryContext.Provider value={registry}>
      {children}
    </RegistryContext.Provider>
  )
}
