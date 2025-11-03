// /app/api/agents/stream/route.ts
export const dynamic = 'force-dynamic'
export const runtime = 'nodejs'
export const revalidate = 0
export const fetchCache = 'force-no-store'

import { exec } from 'node:child_process'
import { promisify } from 'node:util'
import fs from 'node:fs/promises'
import path from 'node:path'

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

async function gatherAgents() {
  try {
    // For realtime display we parse JSON; we can still run a wide command for logs if desired.
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

    return { agents }
  } catch (err) {
    // fallback to static file
    try {
      const fp = path.join(process.cwd(), 'Data', 'do-agents.json')
      const text = await fs.readFile(fp, 'utf-8')
      const parsed = JSON.parse(text)
      return parsed
    } catch (e) {
      return { agents: [] }
    }
  }
}

export async function GET() {
  const encoder = new TextEncoder()
  let interval: NodeJS.Timeout | null = null
  let closed = false
  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      const stop = () => {
        closed = true
        if (interval) {
          clearInterval(interval)
          interval = null
        }
      }

      const send = (obj: any) => {
        if (closed) return
        const payload = `data: ${JSON.stringify(obj)}\n\n`
        try {
          controller.enqueue(encoder.encode(payload))
        } catch (e) {
          // Controller may already be closed; stop further sends
          stop()
        }
      }
      const tick = async () => {
        if (closed) return
        try {
          const data = await gatherAgents()
          send(data)
        } catch {
          // Swallow errors during polling; optionally could emit an error event
        }
      }
      // Initial push
      await tick()
      // Update every 5s
      interval = setInterval(tick, 5000)
    },
    cancel() {
      closed = true
      if (interval) {
        clearInterval(interval)
        interval = null
      }
    },
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
      'X-Accel-Buffering': 'no',
    },
  })
}
