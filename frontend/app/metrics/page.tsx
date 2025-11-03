'use client'

import { Download, TrendingUp, AlertTriangle, Clock } from 'lucide-react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import agentsData from '@/Data/agents.json'

const latencyData = [
  { date: 'Mon', p50: 95, p95: 150, p99: 200 },
  { date: 'Tue', p50: 110, p95: 170, p99: 220 },
  { date: 'Wed', p50: 105, p95: 160, p99: 210 },
  { date: 'Thu', p50: 100, p95: 155, p99: 205 },
  { date: 'Fri', p50: 115, p95: 175, p99: 230 },
  { date: 'Sat', p50: 90, p95: 140, p99: 190 },
  { date: 'Sun', p50: 102, p95: 158, p99: 208 },
]

const requestVolumeData = [
  { hour: '00:00', requests: 120 },
  { hour: '04:00', requests: 85 },
  { hour: '08:00', requests: 450 },
  { hour: '12:00', requests: 680 },
  { hour: '16:00', requests: 520 },
  { hour: '20:00', requests: 380 },
]

const errorRateData = [
  { date: 'Mon', errors: 0.1, success: 99.9 },
  { date: 'Tue', errors: 0.2, success: 99.8 },
  { date: 'Wed', errors: 0.15, success: 99.85 },
  { date: 'Thu', errors: 0.05, success: 99.95 },
  { date: 'Fri', errors: 0.3, success: 99.7 },
  { date: 'Sat', errors: 0.1, success: 99.9 },
  { date: 'Sun', errors: 0.12, success: 99.88 },
]

const deployments = (agentsData as any).agents
  .filter((a: any) => a.deployed)
  .map((a: any) => ({ id: a.id, agent: a.name, version: a.version, deployed: a.deployed, status: a.status || 'healthy' }))

const generatedAgents = (agentsData as any).agents
  .filter((a: any) => a.type && a.language && a.created && a.size)
  .map((a: any) => ({ id: a.id, name: a.name, type: a.type, language: a.language, created: a.created, size: a.size }))

export default function MetricsPage() {
  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-heading font-bold">Detailed Metrics</h1>
          <button className="btn-secondary flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Download Logs</span>
          </button>
        </div>

        {/* Latency Chart */}
        <div className="card mb-8">
          <h2 className="text-2xl font-heading font-bold mb-6 flex items-center space-x-2">
            <TrendingUp className="w-6 h-6 text-accent" />
            <span>Latency Percentiles</span>
          </h2>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={latencyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F1F1F" />
              <XAxis dataKey="date" stroke="#666" />
              <YAxis stroke="#666" label={{ value: 'Latency (ms)', angle: -90, position: 'insideLeft', stroke: '#666' }} />
              <Tooltip contentStyle={{ backgroundColor: '#0F0F0F', border: '1px solid #1F1F1F', color: '#E5E7EB' }} />
              <Legend />
              <Line type="monotone" dataKey="p50" stroke="#EC4899" strokeWidth={2} name="P50" />
              <Line type="monotone" dataKey="p95" stroke="#7C3AED" strokeWidth={2} name="P95" />
              <Line type="monotone" dataKey="p99" stroke="#FACC15" strokeWidth={2} name="P99" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Request Volume */}
          <div className="card">
            <h2 className="text-2xl font-heading font-bold mb-6">Request Volume</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={requestVolumeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F1F1F" />
                <XAxis dataKey="hour" stroke="#666" />
                <YAxis stroke="#666" />
                <Tooltip contentStyle={{ backgroundColor: '#0F0F0F', border: '1px solid #1F1F1F', color: '#E5E7EB' }} />
                <Bar dataKey="requests" fill="#7C3AED" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Error Rate */}
          <div className="card">
            <h2 className="text-2xl font-heading font-bold mb-6 flex items-center space-x-2">
              <AlertTriangle className="w-6 h-6 text-warning" />
              <span>Error Rate vs Success Rate</span>
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={errorRateData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F1F1F" />
                <XAxis dataKey="date" stroke="#666" />
                <YAxis stroke="#666" />
                <Tooltip contentStyle={{ backgroundColor: '#0F0F0F', border: '1px solid #1F1F1F', color: '#E5E7EB' }} />
                <Legend />
                <Line type="monotone" dataKey="errors" stroke="#FACC15" strokeWidth={2} name="Error %" />
                <Line type="monotone" dataKey="success" stroke="#EC4899" strokeWidth={2} name="Success %" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Deployment Timeline */}
        <div className="card mb-8">
          <h2 className="text-2xl font-heading font-bold mb-6 flex items-center space-x-2">
            <Clock className="w-6 h-6 text-secondary" />
            <span>Deployment Timeline</span>
          </h2>
          <div className="space-y-4">
            {deployments.map((deployment: any, index: number) => (
              <div key={deployment.id} className="flex items-center space-x-4">
                <div className="flex flex-col items-center">
                  <div className={`w-4 h-4 rounded-full ${
                    deployment.status === 'healthy' ? 'bg-healthy' :
                    deployment.status === 'warning' ? 'bg-warning' :
                    'bg-deploying'
                  }`}></div>
                  {index < deployments.length - 1 && (
                    <div className="w-0.5 h-16 bg-[#1F1F1F]"></div>
                  )}
                </div>
                <div className="flex-1 bg-[#060606] border border-[#1F1F1F] rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-lg">{deployment.agent}</h3>
                      <p className="text-sm text-text/70">Version {deployment.version}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-text/70">{deployment.deployed}</p>
                      <span className={`text-sm capitalize ${
                        deployment.status === 'healthy' ? 'text-healthy' :
                        deployment.status === 'warning' ? 'text-warning' :
                        'text-deploying'
                      }`}>
                        {deployment.status}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Generated Agents Table */}
        <div className="card">
          <h2 className="text-2xl font-heading font-bold mb-6">Generated Agents</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#1F1F1F]">
                  <th className="text-left py-3 px-4 text-text/70 uppercase text-sm tracking-tight">Name</th>
                  <th className="text-left py-3 px-4 text-text/70 uppercase text-sm tracking-tight">Type</th>
                  <th className="text-left py-3 px-4 text-text/70 uppercase text-sm tracking-tight">Language</th>
                  <th className="text-left py-3 px-4 text-text/70 uppercase text-sm tracking-tight">Created</th>
                  <th className="text-left py-3 px-4 text-text/70 uppercase text-sm tracking-tight">Size</th>
                </tr>
              </thead>
              <tbody>
                {generatedAgents.map((agent: any) => (
                  <tr key={agent.id} className="border-b border-[#1F1F1F] hover:bg-[#0A0A0A] transition-colors">
                    <td className="py-3 px-4 font-semibold">{agent.name}</td>
                    <td className="py-3 px-4 text-text/70">{agent.type}</td>
                    <td className="py-3 px-4 text-text/70">{agent.language}</td>
                    <td className="py-3 px-4 text-text/70">{agent.created}</td>
                    <td className="py-3 px-4 text-text/70">{agent.size}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

