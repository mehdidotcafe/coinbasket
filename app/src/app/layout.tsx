import type { Metadata } from 'next'
import { Analytics } from '@vercel/analytics/next'
import { Providers } from '../providers'
import { Header } from './header'
import './globals.css'

export const metadata: Metadata = {
  title: 'coinbasket',
  description: 'AI-Powered Crypto Orders. One Prompt Away',
  icons: {
    icon: 'favicon/favicon.ico',
    shortcut: 'favicon/favicon.ico',
    apple: 'favicon/apple-touch-icon.png',
    other: {
      rel: 'apple-touch-icon',
      sizes: '180x180',
      url: 'favicon/apple-touch-icon.png',
    },
  },
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
