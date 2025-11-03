"use client"

import { Play, Square, RefreshCw, Trash2, ExternalLink, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import agentsData from '@/Data/do-agents.json'
import { useEffect, useState } from 'react'

const shouldInclude = (a: any) => {
  if (!a?.endpoint) return false
  if (a?.name === 'Do Node') return false
  const model = (typeof a?.agent === 'string' && a.agent) || (typeof a?.model === 'string' && a.model) || ''
  if (model.trim() === '') return false
  return true
}

const initialDeployments = (agentsData as any).agents.filter((a: any) => shouldInclude(a))

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
  const [deployments, setDeployments] = useState<any[]>(initialDeployments)
  const [refreshing, setRefreshing] = useState(false)
  const [live, setLive] = useState(true)

  const handleRefresh = async () => {
    try {
      setRefreshing(true)
      const res = await fetch('/api/agents/refresh', { cache: 'no-store' })
      if (!res.ok) throw new Error(`Refresh failed: ${res.status}`)
      const data = await res.json()
      const list = (data?.agents || []).filter((a: any) => shouldInclude(a))
      setDeployments(list)
    } catch (e) {
      console.error(e)
    } finally {
      setRefreshing(false)
    }
  }

  useEffect(() => {
    if (!live) return
    const es = new EventSource('/api/agents/stream')
    es.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data)
        const list = (data?.agents || []).filter((a: any) => shouldInclude(a))
        setDeployments(list)
      } catch (e) {
        console.error('SSE parse error', e)
      }
    }
    es.onerror = () => {
      es.close()
    }
    return () => {
      es.close()
    }
  }, [live])
  return (
  <div className="min-h-screen py-6 px-3 sm:px-4 lg:px-6">
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-heading font-bold">Deployments</h1>
        <div className="flex items-center gap-2">
          <button
            className="btn-primary rounded-md border border-[#1F1F1F] text-sm px-3 py-1.5"
            onClick={() => setLive((v) => !v)}
          >
            {live ? 'Live: On' : 'Live: Off'}
          </button>
          <button
            className="btn-primary text-sm px-3 py-1.5"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? 'Refreshing…' : 'Refresh'}
          </button>
        </div>
      </div>

      <div className="space-y-5">
        {deployments.map((deployment: any) => (
          <div key={deployment.id} className="card p-4">
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center space-x-2 mb-1">
                  <h2 className="text-lg font-heading font-semibold">{deployment.name}</h2>
                  {getStatusBadge(deployment.status)}
                </div>
                <p className="text-xs text-text/70">Version {deployment.version}</p>
              </div>
              <div className="flex items-center space-x-1">
                {deployment.status === 'healthy' && (
                  <>
                    <button className="p-1.5 hover:bg-[#1F1F1F] rounded-md transition-colors">
                      <Square className="w-4 h-4 text-text/70 hover:text-warning" />
                    </button>
                    <button
                      className="p-1.5 hover:bg-[#1F1F1F] rounded-md transition-colors"
                      onClick={handleRefresh}
                      disabled={refreshing}
                    >
                      <RefreshCw
                        className={`w-4 h-4 ${
                          refreshing
                            ? 'animate-spin text-secondary'
                            : 'text-text/70 hover:text-secondary'
                        }`}
                      />
                    </button>
                  </>
                )}
                <button className="p-1.5 hover:bg-[#1F1F1F] rounded-md transition-colors">
                  <Trash2 className="w-4 h-4 text-text/70 hover:text-red-500" />
                </button>
              </div>
            </div>

            <div className="grid grid-cols-6 sm:grid-cols-3 lg:grid-cols-6 xl:grid-cols-6 gap-3 mb-4">
              <div className="bg-[#060606] border border-[#1F1F1F] rounded-md p-3">
                <p className="text-[10px] text-text/70 uppercase mb-0.5">Uptime</p>
                <p className="text-sm font-semibold">{deployment.uptime || deployment.age || '—'}</p>
              </div>
              <div className="bg-[#060606] border border-[#1F1F1F] rounded-md p-3">
                <p className="text-[10px] text-text/70 uppercase mb-0.5">Region</p>
                <p className="text-sm font-semibold">{deployment.region}</p>
              </div>
              <div className="bg-[#060606] border border-[#1F1F1F] rounded-md p-3">
                <p className="text-[10px] text-text/70 uppercase mb-0.5">Replicas</p>
                <p className="text-sm font-semibold">{deployment.replicas}</p>
              </div>
              <div className="bg-[#060606] border border-[#1F1F1F] rounded-md p-3">
                <p className="text-[10px] text-text/70 uppercase mb-0.5">Usage</p>
                <p className="text-sm font-semibold">{deployment.cpu} / {deployment.memory}</p>
              </div>
              <div className="bg-[#060606] border border-[#1F1F1F] rounded-md p-3">
                <p className="text-[10px] text-text/70 uppercase mb-0.5">Lang</p>
                <p className="text-sm font-semibold">{deployment.language || '—'}</p>
              </div>
              <div className="bg-[#060606] border border-[#1F1F1F] rounded-md p-3">
                <p className="text-[10px] text-text/70 uppercase mb-0.5">Model</p>
                <p className="text-sm font-semibold">{deployment.agent || '—'}</p>
              </div>
            </div>

            <div className="flex items-center space-x-1 pt-3 border-t border-[#1F1F1F]">
              <span className="text-xs text-text/70">Endpoint:</span>
              <span className="text-xs text-white hover:text-accent/80 transition-colors truncate">
                {deployment.endpoint}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
)
}

