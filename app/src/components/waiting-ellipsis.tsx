import { useEffect, useRef, useState } from 'react'

function WaitingEllipsis() {
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const [dotCount, setDotCount] = useState(1)

  useEffect(() => {
    intervalRef.current = setInterval(() => {
      setDotCount(prevCount => (prevCount % 3) + 1)
    }, 400)

    return () => {
      intervalRef.current && clearInterval(intervalRef.current)
    }
  }, [])

  return (
    <>
      <span>{'.'.repeat(dotCount)}</span>
      <span className="invisible">{'.'.repeat(3 - dotCount)}</span>
    </>
  )
}

export default WaitingEllipsis
