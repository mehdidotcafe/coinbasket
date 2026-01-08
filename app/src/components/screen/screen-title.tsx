export function ScreenTitle({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <h1 className="text-3xl font-bold lg:text-4xl font-sofia-sans pb-8">
      {children}
    </h1>
  )
}
