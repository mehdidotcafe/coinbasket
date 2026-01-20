export function ScreenTitle({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <h1 className="text-6xl mt-32 md:mt-64 font-sofia-sans mb-8 text-center">
      {children}
    </h1>
  )
}
