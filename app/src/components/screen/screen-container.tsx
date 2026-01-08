export function ScreenContainer({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen w-6/7 md:w-2/3 xl:w-1/2 mx-auto pb-32">
      {children}
    </div>
  )
}
