'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Terminal } from 'lucide-react'
import CloudShell from './CloudShell'

const Navigation = () => {
  const pathname = usePathname()
  const [isShellOpen, setIsShellOpen] = useState(false)

  const isActive = (path: string) => pathname === path

  return (
    <>
      <nav className="sticky top-0 z-50 bg-primary/95 backdrop-blur-sm border-b border-[#1F1F1F]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center space-x-2 group">
              <Terminal className="w-6 h-6 text-secondary group-hover:text-accent transition-colors" />
              <span className="text-xl font-heading font-bold text-secondary group-hover:text-accent transition-colors">
                ParagonAI
              </span>
            </Link>

            {/* Menu Items */}
            <div className="hidden md:flex items-center space-x-8">
              <Link
                href="/dashboard"
                className={`text-sm font-medium uppercase tracking-tight transition-colors hover:text-accent ${
                  isActive('/dashboard') ? 'text-accent' : 'text-text/70'
                }`}
              >
                Dashboard
              </Link>
              <Link
                href="/deployments"
                className={`text-sm font-medium uppercase tracking-tight transition-colors hover:text-accent ${
                  isActive('/deployments') ? 'text-accent' : 'text-text/70'
                }`}
              >
                Deployments
              </Link>
              <Link
                href="/metrics"
                className={`text-sm font-medium uppercase tracking-tight transition-colors hover:text-accent ${
                  isActive('/metrics') ? 'text-accent' : 'text-text/70'
                }`}
              >
                Metrics
              </Link>
              <Link
                href="/about"
                className={`text-sm font-medium uppercase tracking-tight transition-colors hover:text-accent ${
                  isActive('/about') ? 'text-accent' : 'text-text/70'
                }`}
              >
                About Us
              </Link>
              <Link
                href="/account"
                className={`text-sm font-medium uppercase tracking-tight transition-colors hover:text-accent ${
                  isActive('/account') ? 'text-accent' : 'text-text/70'
                }`}
              >
                Account
              </Link>
            </div>

            {/* CTA Button */}
            <button 
              onClick={() => setIsShellOpen(true)}
              className="btn-primary text-sm px-4 py-2"
            >
              Launch CLI
            </button>
          </div>
        </div>
      </nav>

      <CloudShell isOpen={isShellOpen} onClose={() => setIsShellOpen(false)} />
    </>
  )
}

export default Navigation

