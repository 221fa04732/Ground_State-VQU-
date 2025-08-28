import { ReactNode } from 'react'

export const metadata = {
  title: 'More | GroundState - VQE',
  description: 'A simple Next.js 14 App Router layout with TypeScript',
}

interface RootLayoutProps {
  children: ReactNode
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body className="flex flex-col min-h-screen">
          {children}
      </body>
    </html>
  )
}
