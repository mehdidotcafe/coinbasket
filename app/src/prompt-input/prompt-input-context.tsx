'use client'

import type { ReactNode } from 'react'
import { createContext, useContext, useState } from 'react'

interface PromptInputContextType {
  promptInput: string
  setPromptInput: (input: string) => void
}

const PromptInputContext = createContext<PromptInputContextType | undefined>(undefined)

export function PromptInputProvider({ children, defaultValue }: { children: ReactNode, defaultValue?: string }) {
  const [promptInput, setPromptInput] = useState(defaultValue ?? '')

  return (
    <PromptInputContext.Provider value={{ promptInput, setPromptInput }}>
      {children}
    </PromptInputContext.Provider>
  )
}

export function usePromptInput() {
  const context = useContext(PromptInputContext)
  if (context === undefined) {
    throw new Error('usePromptInput must be used within a PromptInputProvider')
  }
  return context
}
