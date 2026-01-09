export function ScreenContainer({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <div className="items-center flex flex-col px-8 md:px-24 xl:px-64 2xl:px-96 mb-48">
      {children}
    </div>
  )
}
