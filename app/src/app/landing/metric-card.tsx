import type { ReactElement } from 'react'

export function MetricCard({ value, descriptions }: { value: string, descriptions: (string | ReactElement)[] }) {
  return (
    <div className="flex flex-row items-end gap-2">
      <span className="text-[5rem]/32 xs:text-[10rem]/45 md:text-[12rem]/50 4xl:text-[20rem]/70 font-sofia-sans font-extrabold">{value}</span>
      <div className="text-2xl md:text-4xl flex flex-col justify-end h-full mb-[36px]">
        {descriptions.map((desc, index) => (
          <div key={index}>{desc}</div>
        ))}
      </div>
    </div>
  )
}
