'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { X, Copy, Check } from 'lucide-react'
import agentsData from '@/Data/agents.json'

interface CommandOutput {
  id: string
  type: 'command' | 'output' | 'error'
  content: string
  timestamp: Date
}

interface CloudShellProps {
  isOpen: boolean
  onClose: () => void
}

const mockCommands: { [key: string]: (args: string[]) => string } = {
  'paragon init': () => `Initializing ParagonAI workspace...
✓ Created .paragon directory
✓ Configuration file created
✓ Ready to create agents!`,

  'paragon create': (args) => {
    const promptIndex = args.indexOf('--prompt')
    const prompt = promptIndex !== -1 && args[promptIndex + 1] 
      ? args[promptIndex + 1].replace(/"/g, '') 
      : 'Build an API agent'
    
    return `Creating agent with prompt: "${prompt}"
▶ Generating agent code...
✓ agent.py created
✓ Dockerfile created
✓ requirements.txt created
✓ docker-compose.yml created
✓ deploy.yaml created
✔ Agent files generated successfully!
📦 Agent ready for deployment`
  },

  'paragon deploy': (args) => {
    const name = args[0] || 'my-agent'
    return `Deploying agent: ${name}
▶ Building Docker image...
✓ Image built: ${name}:latest
▶ Pushing to registry...
✓ Pushed to registry.paragonai.com/${name}:latest
▶ Deploying to AWS EKS...
✓ Deployment created
✓ Service exposed on port 8000
✔ Agent deployed successfully!
🔗 Endpoint: https://${name}.paragonai.com`
  },

  'paragon logs': (args) => {
    const name = args[0] || 'my-agent'
    return `Fetching logs for: ${name}
[2024-01-18 10:30:15] Agent started
[2024-01-18 10:30:16] Connected to database
[2024-01-18 10:30:17] Listening on 0.0.0.0:8000
[2024-01-18 10:31:22] Received request: POST /generate
[2024-01-18 10:31:23] Response sent: 200 OK
[2024-01-18 10:32:15] Health check: OK`
  },

  'paragon status': () => {
    const agents = (agentsData as any).agents.filter((a: any) => a.status)
    const count = agents.length
    const list = agents
      .slice(0, 10) // keep output concise
      .map((a: any) => `  - ${a.name.replace(/\s+/g, '-').toLowerCase()} (${a.status === 'healthy' ? 'running' : a.status})`)
      .join('\n')
    return `ParagonAI CLI Status:
✓ Connected to ParagonAI Cloud
✓ Authenticated as: user@example.com
✓ Workspace: /home/paragon
✓ Active agents: ${count}
${list}`
  },

  'help': () => {
    return `ParagonAI CLI Commands:
  paragon init              Initialize a new workspace
  paragon create            Create a new agent from prompt
  paragon deploy <name>     Deploy an agent to production
  paragon logs <name>       View agent logs
  paragon status            Show CLI and agent status
  clear                    Clear terminal output
  help                     Show this help message`
  },

  'clear': () => 'CLEAR_SCREEN'
}

export default function CloudShell({ isOpen, onClose }: CloudShellProps) {
  const [input, setInput] = useState('')
  const [outputs, setOutputs] = useState<CommandOutput[]>([
    { id: `welcome-${Date.now()}`, type: 'output', content: 'Welcome to ParagonAI Cloud Shell!', timestamp: new Date() },
    { id: `help-${Date.now()}`, type: 'output', content: 'Type "help" to see available commands.', timestamp: new Date() },
  ])
  const [commandHistory, setCommandHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const outputRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight
    }
  }, [outputs])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return

      if (e.key === 'Escape') {
        onClose()
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        if (commandHistory.length > 0) {
          const newIndex = historyIndex === -1 
            ? commandHistory.length - 1 
            : Math.max(0, historyIndex - 1)
          setHistoryIndex(newIndex)
          setInput(commandHistory[newIndex])
        }
      } else if (e.key === 'ArrowDown') {
        e.preventDefault()
        if (historyIndex !== -1) {
          const newIndex = historyIndex + 1
          if (newIndex >= commandHistory.length) {
            setHistoryIndex(-1)
            setInput('')
          } else {
            setHistoryIndex(newIndex)
            setInput(commandHistory[newIndex])
          }
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, commandHistory, historyIndex, onClose])

  const executeCommand = useCallback((cmd: string) => {
    const trimmedCmd = cmd.trim()
    if (!trimmedCmd) return

    const commandId = `cmd-${Date.now()}-${Math.random()}`
    // Add command to output
    setOutputs(prev => [...prev, {
      id: commandId,
      type: 'command',
      content: trimmedCmd,
      timestamp: new Date()
    }])

    // Add to history
    setCommandHistory(prev => [...prev, trimmedCmd])
    setHistoryIndex(-1)

    // Parse command
    const parts = trimmedCmd.split(' ')
    const baseCommand = parts[0]
    const args = parts.slice(1)

    // Handle special commands
    if (baseCommand === 'clear') {
      setOutputs([])
      return
    }

    // Simulate typing delay
    setTimeout(() => {
      let response = ''
      
      if (baseCommand === 'paragon' && parts[1]) {
        const subCommand = `${baseCommand} ${parts[1]}`
        const handler = mockCommands[subCommand] || mockCommands[`paragon ${parts[1]}`]
        if (handler) {
          response = handler(parts.slice(2))
        } else {
          response = `Error: Unknown command "${parts[1]}". Type "help" for available commands.`
        }
      } else {
        const handler = mockCommands[baseCommand]
        if (handler) {
          response = handler(args)
        } else {
          response = `Command not found: "${baseCommand}". Type "help" for available commands.`
        }
      }

      if (response === 'CLEAR_SCREEN') {
        setOutputs([])
      } else {
        // Animate output character by character
        const outputId = `out-${Date.now()}-${Math.random()}`
        let charIndex = 0
        let timeoutId: NodeJS.Timeout | null = null
        
        const animateOutput = () => {
          if (charIndex < response.length) {
            setOutputs(prev => {
              // Remove the current animating output if it exists
              const filtered = prev.filter(out => out.id !== outputId)
              // Add new partial output with the same ID
              return [...filtered, {
                id: outputId,
                type: 'output',
                content: response.slice(0, charIndex + 1),
                timestamp: new Date()
              }]
            })
            charIndex++
            timeoutId = setTimeout(animateOutput, 20)
          } else {
            // Add final newline for spacing
            setOutputs(prev => [...prev, {
              id: `spacer-${Date.now()}-${Math.random()}`,
              type: 'output',
              content: '',
              timestamp: new Date()
            }])
          }
        }
        animateOutput()
        
        // Cleanup function (though we're not returning it, React will handle cleanup)
        return () => {
          if (timeoutId) clearTimeout(timeoutId)
        }
      }
    }, 300)
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    executeCommand(input)
    setInput('')
  }

  const copyToClipboard = async (text: string, index: number) => {
    await navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  if (!isOpen) return null

  return (
    <div 
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 backdrop-blur-sm transition-opacity"
      onClick={onClose}
    >
      <div 
        className="w-full max-w-4xl h-[80vh] bg-[#060606] border-t border-accent/30 rounded-t-2xl shadow-2xl flex flex-col animate-slide-up"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#1F1F1F]">
          <div className="flex items-center space-x-3">
            <div className="flex space-x-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
            </div>
            <span className="text-text/70 text-sm font-mono">paragon@cloud:~</span>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-[#1F1F1F] rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-text/70 hover:text-text" />
          </button>
        </div>

        {/* Terminal Output */}
        <div 
          ref={outputRef}
          className="flex-1 overflow-y-auto px-6 py-4 font-mono text-sm"
          style={{ 
            fontFamily: 'JetBrains Mono, Fira Code, monospace',
            scrollBehavior: 'smooth'
          }}
        >
          {outputs.map((output) => (
            <div key={output.id} className="mb-2 group">
              {output.type === 'command' && (
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-secondary">paragon@cloud:~$</span>
                  <span className="text-accent">{output.content}</span>
                </div>
              )}
              {output.type === 'output' && output.content && (
                <div className="relative">
                  <pre className="whitespace-pre-wrap text-text/90 leading-relaxed">
                    <span className={
                      output.content.includes('✓') || output.content.includes('✔')
                        ? 'text-secondary'
                        : output.content.includes('▶') || output.content.includes('Error')
                        ? 'text-warning'
                        : output.content.includes('🔗') || output.content.includes('📦')
                        ? 'text-accent'
                        : 'text-text/90'
                    }>{output.content}</span>
                  </pre>
                  <button
                    onClick={() => copyToClipboard(output.content, outputs.indexOf(output))}
                    className="absolute top-0 right-0 opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-[#1F1F1F] rounded"
                  >
                    {copiedIndex === outputs.indexOf(output) ? (
                      <Check className="w-4 h-4 text-secondary" />
                    ) : (
                      <Copy className="w-4 h-4 text-text/50" />
                    )}
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Input */}
        <div className="border-t border-[#1F1F1F] px-6 py-4">
          <form onSubmit={handleSubmit} className="flex items-center space-x-2">
            <span className="text-secondary font-mono">paragon@cloud:~$</span>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 bg-transparent outline-none text-text font-mono text-sm caret-secondary"
              style={{ 
                fontFamily: 'JetBrains Mono, Fira Code, monospace',
                textShadow: '0 0 8px rgba(20, 184, 166, 0.5)'
              }}
              autoComplete="off"
            />
            <div className="w-2 h-5 bg-secondary animate-pulse"></div>
          </form>
        </div>
      </div>
    </div>
  )
}

