'use client'

import Link from 'next/link'
import { Terminal, Github, MessageCircle, Zap, Code, Globe } from 'lucide-react'

export default function AboutPage() {
  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <Terminal className="w-16 h-16 text-accent mx-auto mb-6" />
          <h1 className="text-5xl font-heading font-bold mb-6">
            About <span className="text-gradient">ParagonAI</span>
          </h1>
          <p className="text-xl text-text/70 max-w-2xl mx-auto">
            Empowering developers to deploy GenAI agents from prompt to production with speed, 
            reliability, and intuitive tooling.
          </p>
        </div>

        {/* Purpose Section */}
        <div className="card mb-8">
          <h2 className="text-3xl font-heading font-bold mb-4">Our Purpose</h2>
          <p className="text-text/80 mb-4 leading-relaxed">
            ParagonAI bridges the gap between AI experimentation and production deployment. 
            We believe that deploying AI agents should be as simple as writing a prompt. 
            Our platform combines the power of command-line tools with a comprehensive dashboard 
            to give developers full control over their GenAI agent lifecycle.
          </p>
          <p className="text-text/80 leading-relaxed">
            Whether you're building conversational agents, API services, or data processing pipelines, 
            ParagonAI provides the infrastructure and monitoring tools you need to ship with confidence.
          </p>
        </div>

        {/* Tech Philosophy */}
        <div className="card mb-8">
          <h2 className="text-3xl font-heading font-bold mb-4">Tech Philosophy</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-[#060606] border border-[#1F1F1F] rounded-lg p-6">
              <Zap className="w-8 h-8 text-accent mb-4" />
              <h3 className="text-xl font-semibold mb-2">Speed First</h3>
              <p className="text-text/70">
                From prompt to production in minutes, not days. Optimize for developer velocity.
              </p>
            </div>
            <div className="bg-[#060606] border border-[#1F1F1F] rounded-lg p-6">
              <Code className="w-8 h-8 text-secondary mb-4" />
              <h3 className="text-xl font-semibold mb-2">Developer Experience</h3>
              <p className="text-text/70">
                CLI and dashboard work seamlessly together. Use what you prefer, when you prefer.
              </p>
            </div>
            <div className="bg-[#060606] border border-[#1F1F1F] rounded-lg p-6">
              <Globe className="w-8 h-8 text-highlight mb-4" />
              <h3 className="text-xl font-semibold mb-2">Observability</h3>
              <p className="text-text/70">
                Full visibility into agent performance, health, and resource utilization.
              </p>
            </div>
            <div className="bg-[#060606] border border-[#1F1F1F] rounded-lg p-6">
              <Terminal className="w-8 h-8 text-accent mb-4" />
              <h3 className="text-xl font-semibold mb-2">Open Source</h3>
              <p className="text-text/70">
                Built by developers, for developers. Open, transparent, and community-driven.
              </p>
            </div>
          </div>
        </div>

        {/* CLI + Backend Flow */}
        <div className="card mb-8">
          <h2 className="text-3xl font-heading font-bold mb-4">How It Works</h2>
          <div className="space-y-4">
            <div className="flex items-start space-x-4">
              <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold">1</span>
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-1">Write Your Prompt</h3>
                <p className="text-text/70">
                  Use the ParagonAI CLI to describe your agent in plain English.
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold">2</span>
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-1">Generate Code</h3>
                <p className="text-text/70">
                  Our AI generates production-ready code, Dockerfiles, and deployment configs.
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <div className="w-8 h-8 rounded-full bg-highlight flex items-center justify-center flex-shrink-0">
                <span className="text-primary font-bold">3</span>
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-1">Deploy & Monitor</h3>
                <p className="text-text/70">
                  Deploy with one command, then monitor performance in the dashboard.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Community Section */}
        <div className="card text-center">
          <h2 className="text-3xl font-heading font-bold mb-4">Join Our Community</h2>
          <p className="text-text/70 mb-6">
            Connect with other developers, share ideas, and contribute to the future of GenAI deployment.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary flex items-center justify-center space-x-2"
            >
              <Github className="w-5 h-5" />
              <span>GitHub</span>
            </Link>
            <Link
              href="https://discord.com"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary flex items-center justify-center space-x-2"
            >
              <MessageCircle className="w-5 h-5" />
              <span>Discord</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

