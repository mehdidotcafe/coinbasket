import { useEffect, useState } from 'react'

interface UseTypingPlaceholderOptions {
  placeholders: string[]
  typingSpeed?: number // ms per character
  holdDuration?: number // ms to hold after typing complete
}

export function useTypingPlaceholder({
  placeholders,
  typingSpeed = 60,
  holdDuration = 5000,
}: UseTypingPlaceholderOptions): string {
  const [currentPlaceholder, setCurrentPlaceholder] = useState('')
  const [placeholderIndex, setPlaceholderIndex] = useState(0)
  const [charIndex, setCharIndex] = useState(0)
  const [isTyping, setIsTyping] = useState(true)

  useEffect(() => {
    if (placeholders.length === 0)
      return

    const currentText = placeholders[placeholderIndex]

    if (isTyping) {
      // Typing phase
      if (charIndex < currentText.length) {
        const timeout = setTimeout(() => {
          setCurrentPlaceholder(currentText.slice(0, charIndex + 1))
          setCharIndex(charIndex + 1)
        }, typingSpeed)
        return () => clearTimeout(timeout)
      }
      else {
        // Finished typing, hold for a while
        const timeout = setTimeout(() => {
          setIsTyping(false)
          setCharIndex(0)
          setCurrentPlaceholder('')
          setPlaceholderIndex((placeholderIndex + 1) % placeholders.length)
        }, holdDuration)
        return () => clearTimeout(timeout)
      }
    }
    else {
      // Start typing the next placeholder
      setIsTyping(true)
    }
  }, [charIndex, placeholderIndex, isTyping, placeholders, typingSpeed, holdDuration])

  return currentPlaceholder
}
