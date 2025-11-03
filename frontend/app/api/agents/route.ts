// /app/api/agents/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  const res = await fetch('https://api.digitalocean.com/v2/kubernetes/clusters', {
    headers: {
      Authorization: `Bearer ${process.env.DIGITALOCEAN_API_TOKEN}`,
    },
  })
  const data = await res.json()
  console.log('Fetched DigitalOcean Apps:', data)
  return NextResponse.json(data)
}
