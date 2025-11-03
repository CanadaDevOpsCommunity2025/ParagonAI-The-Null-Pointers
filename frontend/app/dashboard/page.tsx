"use client"

import { Activity, Cpu, HardDrive, Zap, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import agentsData from '@/Data/do-agents.json'
import { useEffect, useState } from 'react'

const shouldInclude = (a: any) => {
  if (!a?.endpoint) return false
  if (a?.name === 'Do Node') return false
  const model = (typeof a?.agent === 'string' && a.agent) || (typeof a?.model === 'string' && a.model) || ''
  if (model.trim() === '') return false
  return true
}

const initialAgents = ((agentsData as any).agents as any[]).filter((a) => shouldInclude(a))
const initialDeployments = initialAgents.map((a: any) => ({
  id: a.id,
  name: a.name,
  version: a.version,
  uptime: a.uptime ?? '—',
  status: a.status,
}))

const agentsList = (agentsData as any).agents as any[]
const a1 = agentsList[0]
const a2 = agentsList[1]
const a3 = agentsList[2]
const warn = agentsList.find(a => a.status === 'warning')
const mockActivity = [
  { id: 1, type: 'build',  message: `${a1?.name ?? 'Agent'} built successfully`, timestamp: '2 minutes ago' },
  { id: 2, type: 'deploy', message: `${a2?.name ?? 'Agent'} deployed to production`, timestamp: '15 minutes ago' },
  { id: 3, type: 'push',   message: `${a3?.name ?? 'Agent'} pushed to registry`, timestamp: '1 hour ago' },
  { id: 4, type: 'error',  message: `${warn?.name ?? 'Agent'} warning: high memory usage`, timestamp: '2 hours ago' },
]

const mockMetrics = [
  { time: '00:00', latency: 120, cpu: 45, memory: 60 },
  { time: '04:00', latency: 95, cpu: 50, memory: 65 },
  { time: '08:00', latency: 150, cpu: 70, memory: 75 },
  { time: '12:00', latency: 110, cpu: 55, memory: 68 },
  { time: '16:00', latency: 130, cpu: 65, memory: 72 },
  { time: '20:00', latency: 100, cpu: 48, memory: 58 },
]

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'healthy':
      return <CheckCircle className="w-5 h-5 text-healthy" />
    case 'deploying':
      return <Clock className="w-5 h-5 text-deploying animate-pulse" />
    case 'warning':
      return <AlertCircle className="w-5 h-5 text-warning" />
    default:
      return null
  }
}

export default function DashboardPage() {
  const [active, setActive] = useState<any[]>(initialDeployments)
  // Mocked, click-driven stats state
  const [responseTime, setResponseTime] = useState<number>(112)
  const [successRate, setSuccessRate] = useState<number>(99.8)
  const [totalRequests, setTotalRequests] = useState<number>(12400)
  const [activity, setActivity] = useState<any[]>(mockActivity)
  const [metrics, setMetrics] = useState<any[]>(mockMetrics)

  const rand = (min: number, max: number) => Math.random() * (max - min) + min
  const randInt = (min: number, max: number) => Math.floor(rand(min, max))

  const randomizeMetrics = () => {
    const times = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
    const gen = times.map((t) => ({
      time: t,
      latency: Math.round(rand(80, 220)),
      cpu: Math.round(rand(25, 90)),
      memory: Math.round(rand(35, 90)),
    }))
    setMetrics(gen)
  }

  const onAgentClick = (agent: any) => {
    // Randomize KPI cards
    setResponseTime(Math.round(rand(70, 210)))
    setSuccessRate(parseFloat(rand(95, 99.95).toFixed(2)))
    // Increment/decrement requests a bit to simulate traffic
    const delta = randInt(-1200, 2200)
    setTotalRequests((prev) => Math.max(0, prev + delta))
    // Add a fresh recent activity entry to the top
    const variants = ['handled', 'processed', 'served', 'completed']
    const action = variants[randInt(0, variants.length)]
    const reqCount = Math.max(1, randInt(50, 800))
    const newEvent = {
      id: Date.now(),
      type: delta < 0 ? 'error' : 'deploy',
      message: `${agent.name} ${action} ${reqCount.toLocaleString()} requests`,
      timestamp: 'just now',
    }
    setActivity((prev) => [newEvent, ...prev].slice(0, 12))
    // Update the utilization charts
    randomizeMetrics()
  }

  useEffect(() => {
    const es = new EventSource('/api/agents/stream')
    es.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data)
        const list = (data?.agents || [])
          .filter((a: any) => shouldInclude(a))
          .map((a: any) => ({ id: a.id, name: a.name, version: a.version, uptime: a.uptime ?? '—', status: a.status }))
        setActive(list)
      } catch (e) {
        console.error('SSE parse error', e)
      }
    }
    es.onerror = () => es.close()
    return () => es.close()
  }, [])
  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-heading font-bold mb-8">Dashboard</h1>

        {/* Metrics Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <span className="text-text/70 text-sm uppercase tracking-tight">Response Time</span>
              <Zap className="w-5 h-5 text-accent" />
            </div>
            <div className="text-3xl font-bold text-text">{responseTime}ms</div>
            <div className="text-sm text-healthy mt-2">Live mock · click an agent</div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <span className="text-text/70 text-sm uppercase tracking-tight">Success Rate</span>
              <CheckCircle className="w-5 h-5 text-healthy" />
            </div>
            <div className="text-3xl font-bold text-text">{successRate.toFixed(2)}%</div>
            <div className="text-sm text-healthy mt-2">Live mock · click an agent</div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <span className="text-text/70 text-sm uppercase tracking-tight">Total Requests</span>
              <Activity className="w-5 h-5 text-secondary" />
            </div>
            <div className="text-3xl font-bold text-text">{Intl.NumberFormat('en', { notation: 'compact' }).format(totalRequests)}</div>
            <div className="text-sm text-secondary mt-2">Last 24 hours · mock</div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <span className="text-text/70 text-sm uppercase tracking-tight">Active Agents</span>
              <Activity className="w-5 h-5 text-highlight" />
            </div>
            <div className="text-3xl font-bold text-text">{active.length}</div>
            <div className="text-sm text-text/70 mt-2">Currently running</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Active Deployments */}
          <div className="card">
            <h2 className="text-2xl font-heading font-bold mb-6">Active Deployments</h2>
            <div className="space-y-4">
              {active.map((deployment: any) => (
                <div
                  key={deployment.id}
                  className="bg-[#060606] border border-[#1F1F1F] rounded-lg p-4 hover:border-accent/50 transition-colors cursor-pointer"
                  onClick={() => onAgentClick(deployment)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-semibold text-lg">{deployment.name}</h3>
                      <p className="text-sm text-text/70">v{deployment.version}</p>
                    </div>
                    {getStatusIcon(deployment.status)}
                  </div>
                  <div className="flex items-center space-x-4 mt-3 text-sm">
                    <span className="text-text/70">Uptime: {deployment.uptime}</span>
                    <span className={`capitalize ${
                      deployment.status === 'healthy' ? 'text-healthy' :
                      deployment.status === 'deploying' ? 'text-deploying' :
                      'text-warning'
                    }`}>
                      {deployment.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="card">
            <h2 className="text-2xl font-heading font-bold mb-6">Recent Activity</h2>
            <div className="space-y-4">
              {activity.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-start space-x-3 pb-4 border-b border-[#1F1F1F] last:border-0"
                >
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    activity.type === 'error' ? 'bg-warning' :
                    activity.type === 'deploy' ? 'bg-accent' :
                    activity.type === 'build' ? 'bg-healthy' :
                    'bg-secondary'
                  }`}></div>
                  <div className="flex-1">
                    <p className="text-sm text-text">{activity.message}</p>
                    <p className="text-xs text-text/50 mt-1">{activity.timestamp}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Resource Utilization */}
        <div className="card">
          <h2 className="text-2xl font-heading font-bold mb-6">Resource Utilization</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Cpu className="w-5 h-5 text-accent" />
                <h3 className="font-semibold">CPU Usage</h3>
              </div>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={metrics}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1F1F1F" />
                  <XAxis dataKey="time" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip contentStyle={{ backgroundColor: '#0F0F0F', border: '1px solid #1F1F1F' }} />
                  <Area type="monotone" dataKey="cpu" stroke="#7C3AED" fill="#7C3AED" fillOpacity={0.2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div>
              <div className="flex items-center space-x-2 mb-4">
                <HardDrive className="w-5 h-5 text-secondary" />
                <h3 className="font-semibold">Memory Usage</h3>
              </div>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={metrics}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1F1F1F" />
                  <XAxis dataKey="time" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip contentStyle={{ backgroundColor: '#0F0F0F', border: '1px solid #1F1F1F' }} />
                  <Area type="monotone" dataKey="memory" stroke="#EC4899" fill="#EC4899" fillOpacity={0.2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Zap className="w-5 h-5 text-highlight" />
                <h3 className="font-semibold">Latency</h3>
              </div>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={metrics}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1F1F1F" />
                  <XAxis dataKey="time" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip contentStyle={{ backgroundColor: '#0F0F0F', border: '1px solid #1F1F1F' }} />
                  <Line type="monotone" dataKey="latency" stroke="#FACC15" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

