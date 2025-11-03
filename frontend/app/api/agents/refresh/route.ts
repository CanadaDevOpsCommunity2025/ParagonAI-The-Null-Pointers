// /app/api/agents/refresh/route.ts
export const dynamic = 'force-dynamic'
export const runtime = 'nodejs'
export const revalidate = 0
export const fetchCache = 'force-no-store'
import { NextResponse } from 'next/server'
import { exec } from 'node:child_process'
import { promisify } from 'node:util'
import path from 'node:path'
import fs from 'node:fs/promises'

const execAsync = promisify(exec)

type K8sList<T> = { items: T[] }
type Pod = {
  metadata: {
    name: string
    namespace: string
    creationTimestamp?: string
    annotations?: Record<string, string>
    labels?: Record<string, string>
  }
  spec: { nodeName?: string; containers: Array<{ name: string; resources?: any }> }
  status: { phase?: string; podIP?: string; startTime?: string }
}
type NodeItem = {
  metadata: { name: string; labels?: Record<string, string> }
}

function toTitle(s: string) {
  return s
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

function formatUptime(fromIso?: string) {
  if (!fromIso) return ''
  const start = new Date(fromIso).getTime()
  const now = Date.now()
  const diff = Math.max(0, now - start)
  const mins = Math.floor(diff / 60000)
  const days = Math.floor(mins / (60 * 24))
  const hours = Math.floor((mins % (60 * 24)) / 60)
  const minutes = mins % 60
  const parts: string[] = []
  if (days) parts.push(`${days}d`)
  if (hours) parts.push(`${hours}h`)
  parts.push(`${minutes}m`)
  return parts.join(' ')
}

function phaseToStatus(phase?: string) {
  switch ((phase || '').toLowerCase()) {
    case 'running':
      return 'healthy'
    case 'pending':
      return 'deploying'
    case 'failed':
    case 'unknown':
      return 'warning'
    default:
      return 'deploying'
  }
}

export async function GET() {
  try {
    // Try kubectl first
    const [{ stdout: podsJson }, { stdout: nodesJson }] = await Promise.all([
      execAsync('kubectl get pods --all-namespaces -o json'),
      execAsync('kubectl get nodes -o json'),
    ])

    const pods = JSON.parse(podsJson) as K8sList<Pod>
    const nodes = JSON.parse(nodesJson) as K8sList<NodeItem>

    const nodeRegion = new Map<string, string>()
    for (const n of nodes.items || []) {
      const labels = n.metadata?.labels || {}
      nodeRegion.set(
        n.metadata?.name,
        labels['topology.kubernetes.io/region'] || labels['failure-domain.beta.kubernetes.io/region'] || labels['region'] || ''
      )
    }

    let id = 1
    const agents = (pods.items || [])
      .filter((p) => {
        const labels = p.metadata?.labels || {}
        const anns = p.metadata?.annotations || {}
        const app = labels['app'] || ''
        const agentType = labels['agent-type'] || ''
        const hasMarker = app.includes('agent') || agentType || anns['agent-id']
        // exclude obvious infra like mongodb
        const isInfra = app.includes('mongodb') || labels['app'] === 'mongodb'
        return hasMarker && !isInfra
      })
      .map((p) => {
        const labels = p.metadata?.labels || {}
        const anns = p.metadata?.annotations || {}
        const appLabel = labels['app'] || p.metadata?.name || 'agent'
        const base = appLabel.replace(/-agent$/, '')
        const type = labels['agent-type'] || base.replace(/-?agent$/, '')
        const name = `${toTitle(base.replace(/-?agent$/, ''))} Agent`
        const model = anns['agent-model'] || ''
        const created = p.metadata?.creationTimestamp ? new Date(p.metadata.creationTimestamp).toISOString().slice(0, 10) : ''
        const uptime = formatUptime(p.status?.startTime)
        const region = nodeRegion.get(p.spec?.nodeName || '') || ''
        const container = p.spec.containers?.[0]
        const limits = container?.resources?.limits || {}
        const cpu = limits.cpu || ''
        const memory = limits.memory || ''

        return {
          id: id++,
          name,
          version: '1.0.0',
          status: phaseToStatus(p.status?.phase),
          uptime,
          endpoint: p.status?.podIP ? `http://${p.status.podIP}` : '',
          region,
          replicas: 1,
          cpu: String(cpu || ''),
          memory: String(memory || ''),
          type,
          language: 'Python',
          created,
          size: 'N/A',
          agent: model || '',
          deployed: 'testing',
          node: p.spec?.nodeName || '',
        }
      })

    return NextResponse.json({ agents })
  } catch (err) {
    // Fallback to static file if kubectl not available
    try {
      const fp = path.join(process.cwd(), 'Data', 'do-agents.json')
      const text = await fs.readFile(fp, 'utf-8')
      const parsed = JSON.parse(text)
      return NextResponse.json(parsed)
    } catch (e) {
      return NextResponse.json({ agents: [] })
    }
  }
}
