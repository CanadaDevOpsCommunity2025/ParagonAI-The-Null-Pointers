'use client'

import { useState } from 'react'
import { User, Key, Settings, Moon, Sun, Save, Eye, EyeOff } from 'lucide-react'

export default function AccountPage() {
  const [showApiKey, setShowApiKey] = useState(false)
  const [theme, setTheme] = useState<'dark' | 'light'>('dark')
  const [apiKey, setApiKey] = useState('pk_live_••••••••••••••••••••••••')
  
  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-heading font-bold mb-8">Account Settings</h1>

        {/* Profile Section */}
        <div className="card mb-8">
          <div className="flex items-center space-x-4 mb-6">
            <User className="w-8 h-8 text-accent" />
            <h2 className="text-2xl font-heading font-bold">Profile</h2>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text/70 mb-2 uppercase tracking-tight">
                Name
              </label>
              <input
                type="text"
                defaultValue="John Doe"
                className="w-full bg-[#060606] border border-[#1F1F1F] rounded-lg px-4 py-2 text-text focus:outline-none focus:border-accent transition-colors"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text/70 mb-2 uppercase tracking-tight">
                Email
              </label>
              <input
                type="email"
                defaultValue="john.doe@example.com"
                className="w-full bg-[#060606] border border-[#1F1F1F] rounded-lg px-4 py-2 text-text focus:outline-none focus:border-accent transition-colors"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text/70 mb-2 uppercase tracking-tight">
                Organization
              </label>
              <input
                type="text"
                defaultValue="Acme Corp"
                className="w-full bg-[#060606] border border-[#1F1F1F] rounded-lg px-4 py-2 text-text focus:outline-none focus:border-accent transition-colors"
              />
            </div>
          </div>
        </div>

        {/* CLI Credentials */}
        <div className="card mb-8">
          <div className="flex items-center space-x-4 mb-6">
            <Key className="w-8 h-8 text-secondary" />
            <h2 className="text-2xl font-heading font-bold">CLI Credentials</h2>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text/70 mb-2 uppercase tracking-tight">
                API Token
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type={showApiKey ? 'text' : 'password'}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="flex-1 bg-[#060606] border border-[#1F1F1F] rounded-lg px-4 py-2 text-text focus:outline-none focus:border-accent transition-colors font-mono text-sm"
                />
                <button
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="p-2 hover:bg-[#1F1F1F] rounded-lg transition-colors"
                >
                  {showApiKey ? <EyeOff className="w-5 h-5 text-text/70" /> : <Eye className="w-5 h-5 text-text/70" />}
                </button>
              </div>
              <p className="text-xs text-text/50 mt-2">
                Use this token to authenticate the ParagonAI CLI. Keep it secure.
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-text/70 mb-2 uppercase tracking-tight">
                CLI Endpoint
              </label>
              <input
                type="text"
                defaultValue="https://api.paragonai.com"
                className="w-full bg-[#060606] border border-[#1F1F1F] rounded-lg px-4 py-2 text-text focus:outline-none focus:border-accent transition-colors font-mono text-sm"
              />
            </div>
          </div>
        </div>

        {/* Deployment Preferences */}
        <div className="card mb-8">
          <div className="flex items-center space-x-4 mb-6">
            <Settings className="w-8 h-8 text-highlight" />
            <h2 className="text-2xl font-heading font-bold">Deployment Preferences</h2>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text/70 mb-2 uppercase tracking-tight">
                Default Region
              </label>
              <select className="w-full bg-[#060606] border border-[#1F1F1F] rounded-lg px-4 py-2 text-text focus:outline-none focus:border-accent transition-colors">
                <option value="us-east-1">US East (N. Virginia)</option>
                <option value="us-west-2">US West (Oregon)</option>
                <option value="eu-central-1">Europe (Frankfurt)</option>
                <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-text/70 mb-2 uppercase tracking-tight">
                Default Replicas
              </label>
              <input
                type="number"
                defaultValue={2}
                min={1}
                max={10}
                className="w-full bg-[#060606] border border-[#1F1F1F] rounded-lg px-4 py-2 text-text focus:outline-none focus:border-accent transition-colors"
              />
            </div>
            <div className="flex items-center space-x-4">
              <input
                type="checkbox"
                id="auto-scaling"
                defaultChecked
                className="w-4 h-4 bg-[#060606] border-[#1F1F1F] rounded focus:ring-accent focus:ring-2"
              />
              <label htmlFor="auto-scaling" className="text-sm text-text/70">
                Enable auto-scaling
              </label>
            </div>
          </div>
        </div>

        {/* Theme Settings */}
        <div className="card mb-8">
          <div className="flex items-center space-x-4 mb-6">
            {theme === 'dark' ? <Moon className="w-8 h-8 text-accent" /> : <Sun className="w-8 h-8 text-highlight" />}
            <h2 className="text-2xl font-heading font-bold">Appearance</h2>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setTheme('dark')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-colors ${
                theme === 'dark'
                  ? 'border-accent bg-accent/10 text-accent'
                  : 'border-[#1F1F1F] bg-[#060606] text-text/70 hover:border-accent/50'
              }`}
            >
              <Moon className="w-4 h-4" />
              <span>Dark</span>
            </button>
            <button
              onClick={() => setTheme('light')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-colors ${
                theme === 'light'
                  ? 'border-highlight bg-highlight/10 text-highlight'
                  : 'border-[#1F1F1F] bg-[#060606] text-text/70 hover:border-highlight/50'
              }`}
            >
              <Sun className="w-4 h-4" />
              <span>Light</span>
            </button>
          </div>
          <p className="text-xs text-text/50 mt-4">
            Note: Light theme is coming soon. Currently using Neo-Synth dark theme.
          </p>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button className="btn-primary flex items-center space-x-2">
            <Save className="w-4 h-4" />
            <span>Save Changes</span>
          </button>
        </div>
      </div>
    </div>
  )
}

