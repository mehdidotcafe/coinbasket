import { useEffect, useRef } from 'react'

export function useResettableInterval(callback: () => void, delay: number) {
  const savedCallback = useRef(callback)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    savedCallback.current = callback
  }, [callback])

  const stop = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }
  }

  const start = () => {
    stop()
    intervalRef.current = setInterval(() => {
      return savedCallback.current()
    }, delay)
  }

  const reset = () => {
    start()
  }

  useEffect(() => {
    start()
    return stop
  }, [delay])

  return { resetInterval: reset, stopInterval: stop }
}
