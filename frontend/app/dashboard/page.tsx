'use client'

import { Activity, Cpu, HardDrive, Zap, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const mockDeployments = [
  { id: 1, name: 'API Agent v2.1', version: '2.1.0', uptime: '12d 4h', status: 'healthy' },
  { id: 2, name: 'Chat Bot Agent', version: '1.3.5', uptime: '5d 8h', status: 'healthy' },
  { id: 3, name: 'Data Processor', version: '3.0.2', uptime: '2h 15m', status: 'deploying' },
  { id: 4, name: 'Legacy Agent', version: '1.0.0', uptime: '1d 2h', status: 'warning' },
]

const mockActivity = [
  { id: 1, type: 'build', message: 'API Agent v2.1 built successfully', timestamp: '2 minutes ago' },
  { id: 2, type: 'deploy', message: 'Chat Bot Agent deployed to production', timestamp: '15 minutes ago' },
  { id: 3, type: 'push', message: 'Data Processor pushed to registry', timestamp: '1 hour ago' },
  { id: 4, type: 'error', message: 'Legacy Agent warning: high memory usage', timestamp: '2 hours ago' },
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
            <div className="text-3xl font-bold text-text">112ms</div>
            <div className="text-sm text-healthy mt-2">↓ 12% from last hour</div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <span className="text-text/70 text-sm uppercase tracking-tight">Success Rate</span>
              <CheckCircle className="w-5 h-5 text-healthy" />
            </div>
            <div className="text-3xl font-bold text-text">99.8%</div>
            <div className="text-sm text-healthy mt-2">↑ 0.2% from last hour</div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <span className="text-text/70 text-sm uppercase tracking-tight">Total Requests</span>
              <Activity className="w-5 h-5 text-secondary" />
            </div>
            <div className="text-3xl font-bold text-text">12.4K</div>
            <div className="text-sm text-secondary mt-2">Last 24 hours</div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <span className="text-text/70 text-sm uppercase tracking-tight">Active Agents</span>
              <Activity className="w-5 h-5 text-highlight" />
            </div>
            <div className="text-3xl font-bold text-text">{mockDeployments.length}</div>
            <div className="text-sm text-text/70 mt-2">Currently running</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Active Deployments */}
          <div className="card">
            <h2 className="text-2xl font-heading font-bold mb-6">Active Deployments</h2>
            <div className="space-y-4">
              {mockDeployments.map((deployment) => (
                <div
                  key={deployment.id}
                  className="bg-[#060606] border border-[#1F1F1F] rounded-lg p-4 hover:border-accent/50 transition-colors"
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
              {mockActivity.map((activity) => (
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
                <AreaChart data={mockMetrics}>
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
                <AreaChart data={mockMetrics}>
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
                <LineChart data={mockMetrics}>
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

