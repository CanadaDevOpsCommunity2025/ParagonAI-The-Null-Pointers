'use client'

import Link from 'next/link'
import { ArrowRight, Terminal } from 'lucide-react'
import { useState, useEffect } from 'react'
import BlurText from '@/components/BlurText'

export default function Home() {
  const [terminalText, setTerminalText] = useState('')
  const commands = [
    'paragon create --prompt "Build an API agent"',
    'paragon deploy --name "api-agent"',
    'paragon status --all'
  ]

  const handleAnimationComplete = () => {
    console.log('Animation completed!')
  }

  useEffect(() => {
    let commandIndex = 0
    let charIndex = 0
    let timeoutId: NodeJS.Timeout | null = null

    const typeNextChar = () => {
      const currentCommand = commands[commandIndex]
      
      if (charIndex < currentCommand.length) {
        // Typing out current command
        setTerminalText(currentCommand.slice(0, charIndex + 1))
        charIndex++
        timeoutId = setTimeout(typeNextChar, 100)
      } else {
        // Current command finished, wait before next command
        timeoutId = setTimeout(() => {
          commandIndex = (commandIndex + 1) % commands.length
          charIndex = 0
          setTerminalText('')
          typeNextChar()
        }, 1500) // Wait 1.5 seconds before starting next command
      }
    }

    typeNextChar()

    return () => {
      if (timeoutId) clearTimeout(timeoutId)
    }
  }, [])

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-32 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-5xl md:text-7xl font-heading font-bold mb-6 leading-tight">
              <span className="text-gradient">
                Deploy GenAI Agents
              </span>
              <br />
              {/* <span className="text-text">from Prompt to Production</span> */}
              <div className="flex justify-center mt-6 text-text text-6xl">
                <BlurText
                text="from Prompt to Production"
                delay={50}
                animateBy="letters"
                direction="bottom"
                onAnimationComplete={handleAnimationComplete}
                />
              </div>
            </h1>
            
            <p className="text-xl md:text-2xl text-text/70 max-w-3xl mx-auto mb-12">
              Seamlessly build, deploy, and monitor intelligent AI agents using the ParagonAI CLI 
              and dashboard. From a simple prompt to a fully deployed production agent in minutes.
            </p>

            {/* Animated Terminal Mockup */}
            <div className="max-w-3xl mx-auto mb-12">
              <div className="bg-[#0F0F0F] border border-[#1F1F1F] rounded-lg p-6 text-left">
                <div className="flex items-center space-x-2 mb-4">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  <span className="ml-4 text-text/50 text-sm">Terminal</span>
                </div>
                <div className="font-mono text-text">
                  <span className="text-secondary">$</span>{' '}
                  <span className="text-accent">{terminalText}</span>
                  <span className="animate-pulse">|</span>
                </div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="/dashboard" className="btn-primary flex items-center space-x-2">
                <span>Get Started</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link href="/dashboard" className="btn-secondary flex items-center space-x-2">
                <span>View Dashboard</span>
                <Terminal className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>

        {/* Background Effects */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-accent/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-3xl"></div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-[#0A0A0A]">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-heading font-bold text-center mb-12">
            Powerful Features
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="card">
              <Terminal className="w-8 h-8 text-accent mb-4" />
              <h3 className="text-xl font-semibold mb-2">CLI Integration</h3>
              <p className="text-text/70">
                Powerful command-line tools to create and manage agents from your terminal.
              </p>
            </div>
            <div className="card">
              <div className="w-8 h-8 bg-secondary rounded-full mb-4 flex items-center justify-center">
                <div className="w-3 h-3 bg-primary rounded-full"></div>
              </div>
              <h3 className="text-xl font-semibold mb-2">Real-time Monitoring</h3>
              <p className="text-text/70">
                Track performance, health, and metrics of all your deployed agents.
              </p>
            </div>
            <div className="card">
              <div className="w-8 h-8 bg-highlight rounded-full mb-4 flex items-center justify-center">
                <div className="w-3 h-3 bg-primary rounded-full"></div>
              </div>
              <h3 className="text-xl font-semibold mb-2">Fast Deployment</h3>
              <p className="text-text/70">
                Deploy from prompt to production in minutes with automated workflows.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

