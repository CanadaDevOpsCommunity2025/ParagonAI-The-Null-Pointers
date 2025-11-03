import { NextResponse } from 'next/server'

// Placeholder API route for metrics
// This should be connected to your backend API

export async function GET() {
  // Mock data - replace with actual API call to backend
  const metrics = {
    responseTime: 112,
    successRate: 99.8,
    totalRequests: 12400,
    activeAgents: 4,
    latency: {
      p50: 95,
      p95: 150,
      p99: 200,
    },
    resources: {
      cpu: 55,
      memory: 68,
    },
  }

  return NextResponse.json(metrics)
}

