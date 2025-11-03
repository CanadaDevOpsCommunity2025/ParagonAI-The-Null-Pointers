import type { Metadata } from 'next'
import { Inter, Poppins } from 'next/font/google'
import './globals.css'
import Navigation from '@/components/Navigation'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const poppins = Poppins({ 
  subsets: ['latin'], 
  weight: ['600', '700', '800'],
  variable: '--font-poppins' 
})

export const metadata: Metadata = {
  title: 'ParagonAI - Deploy GenAI Agents from Prompt to Production',
  description: 'Dashboard for managing and monitoring GenAI agent deployments',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${poppins.variable}`}>
      <body className="min-h-screen bg-primary text-text">
        <Navigation />
        <main className="transition-opacity duration-300">
          {children}
        </main>
      </body>
    </html>
  )
}

