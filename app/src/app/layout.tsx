import type { Metadata } from 'next'
import { Analytics } from '@vercel/analytics/next'
import { Providers } from '../providers'
import { Header } from './header'
import './globals.css'

export const metadata: Metadata = {
  title: 'coinbasket',
  description: 'Be free to invest',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body
        className="antialiased"
      >
        <Providers>
          <div className="flex flex-col w-full">
            <Header />
            {children}
          </div>
        </Providers>
        <Analytics />
      </body>
    </html>
  )
}
