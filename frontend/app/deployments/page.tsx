'use client'

import { Play, Square, RefreshCw, Trash2, ExternalLink, CheckCircle, Clock, AlertCircle } from 'lucide-react'

const deployments = [
  { 
    id: 1, 
    name: 'API Agent v2.1', 
    version: '2.1.0', 
    status: 'healthy', 
    uptime: '12d 4h 32m',
    endpoint: 'https://api-agent.example.com',
    region: 'us-east-1',
    replicas: 3,
    cpu: '45%',
    memory: '2.1 GB'
  },
  { 
    id: 2, 
    name: 'Chat Bot Agent', 
    version: '1.3.5', 
    status: 'healthy', 
    uptime: '5d 8h 15m',
    endpoint: 'https://chatbot.example.com',
    region: 'us-west-2',
    replicas: 2,
    cpu: '32%',
    memory: '1.8 GB'
  },
  { 
    id: 3, 
    name: 'Data Processor', 
    version: '3.0.2', 
    status: 'deploying', 
    uptime: '2h 15m',
    endpoint: 'https://data-processor.example.com',
    region: 'eu-central-1',
    replicas: 1,
    cpu: '67%',
    memory: '3.2 GB'
  },
  { 
    id: 4, 
    name: 'Legacy Agent', 
    version: '1.0.0', 
    status: 'warning', 
    uptime: '1d 2h 8m',
    endpoint: 'https://legacy.example.com',
    region: 'us-east-1',
    replicas: 1,
    cpu: '89%',
    memory: '4.5 GB'
  },
]

const getStatusBadge = (status: string) => {
  const config = {
    healthy: { icon: CheckCircle, color: 'text-healthy', bg: 'bg-healthy/10', border: 'border-healthy/30' },
    deploying: { icon: Clock, color: 'text-deploying', bg: 'bg-deploying/10', border: 'border-deploying/30' },
    warning: { icon: AlertCircle, color: 'text-warning', bg: 'bg-warning/10', border: 'border-warning/30' },
  }
  
  const { icon: Icon, color, bg, border } = config[status as keyof typeof config] || config.healthy
  
  return (
    <span className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${bg} ${border} border ${color}`}>
      <Icon className="w-4 h-4" />
      <span className="capitalize">{status}</span>
    </span>
  )
}

export default function DeploymentsPage() {
  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-heading font-bold">Deployments</h1>
          <button className="btn-primary">New Deployment</button>
        </div>

        <div className="space-y-6">
          {deployments.map((deployment) => (
            <div key={deployment.id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center space-x-3 mb-2">
                    <h2 className="text-2xl font-heading font-bold">{deployment.name}</h2>
                    {getStatusBadge(deployment.status)}
                  </div>
                  <p className="text-text/70">Version {deployment.version}</p>
                </div>
                <div className="flex items-center space-x-2">
                  {deployment.status === 'healthy' && (
                    <>
                      <button className="p-2 hover:bg-[#1F1F1F] rounded-lg transition-colors">
                        <Square className="w-5 h-5 text-text/70 hover:text-warning" />
                      </button>
                      <button className="p-2 hover:bg-[#1F1F1F] rounded-lg transition-colors">
                        <RefreshCw className="w-5 h-5 text-text/70 hover:text-secondary" />
                      </button>
                    </>
                  )}
                  <button className="p-2 hover:bg-[#1F1F1F] rounded-lg transition-colors">
                    <Trash2 className="w-5 h-5 text-text/70 hover:text-red-500" />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                <div className="bg-[#060606] border border-[#1F1F1F] rounded-lg p-4">
                  <p className="text-sm text-text/70 uppercase tracking-tight mb-1">Uptime</p>
                  <p className="text-lg font-semibold">{deployment.uptime}</p>
                </div>
                <div className="bg-[#060606] border border-[#1F1F1F] rounded-lg p-4">
                  <p className="text-sm text-text/70 uppercase tracking-tight mb-1">Region</p>
                  <p className="text-lg font-semibold">{deployment.region}</p>
                </div>
                <div className="bg-[#060606] border border-[#1F1F1F] rounded-lg p-4">
                  <p className="text-sm text-text/70 uppercase tracking-tight mb-1">Replicas</p>
                  <p className="text-lg font-semibold">{deployment.replicas}</p>
                </div>
                <div className="bg-[#060606] border border-[#1F1F1F] rounded-lg p-4">
                  <p className="text-sm text-text/70 uppercase tracking-tight mb-1">Resource Usage</p>
                  <p className="text-lg font-semibold">{deployment.cpu} / {deployment.memory}</p>
                </div>
              </div>

              <div className="flex items-center space-x-2 pt-4 border-t border-[#1F1F1F]">
                <ExternalLink className="w-4 h-4 text-text/70" />
                <a 
                  href={deployment.endpoint} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-accent hover:text-accent/80 transition-colors text-sm"
                >
                  {deployment.endpoint}
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

