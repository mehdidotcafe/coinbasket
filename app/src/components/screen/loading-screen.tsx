import { Loader } from '@/loader'

export function LoadingScreen() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen w-6/7 md:w-2/3 xl:w-1/2 mx-auto">
      <Loader width={64} height={64} />
    </div>
  )
}
