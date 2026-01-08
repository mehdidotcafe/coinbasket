import Image from 'next/image'

interface Props {
  width: number
  height: number
}

export function Loader({
  width,
  height,
}: Props) {
  return (
    <Image
      className="loader"
      src="/logo/coinbasket.svg"
      height={height}
      width={width}
      alt="loader"
      role="status"
    />
  )
}
