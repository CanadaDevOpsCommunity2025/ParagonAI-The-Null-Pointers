'use client'

import { useState } from 'react'
import { FileCode, Folder, ChevronRight, ChevronDown, File, Settings, Box } from 'lucide-react'

interface FileNode {
  name: string
  type: 'file' | 'folder'
  content?: string
  children?: FileNode[]
}

const projectFiles: FileNode = {
  name: 'agent-project',
  type: 'folder',
  children: [
    {
      name: 'src',
      type: 'folder',
      children: [
        {
          name: 'agent.py',
          type: 'file',
          content: `from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="GenAI Agent API")

class Request(BaseModel):
    prompt: str
    context: dict = {}

@app.post("/generate")
async def generate(request: Request):
    # Agent logic here
    return {"response": "Generated content"}
`
        },
        {
          name: 'config.py',
          type: 'file',
          content: `# Agent Configuration
API_KEY = os.getenv("API_KEY")
MODEL = "gpt-4"
TEMPERATURE = 0.7
`
        }
      ]
    },
    {
      name: 'Dockerfile',
      type: 'file',
      content: `FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.agent:app", "--host", "0.0.0.0", "--port", "8000"]
`
    },
    {
      name: 'requirements.txt',
      type: 'file',
      content: `fastapi==0.104.0
uvicorn==0.24.0
pydantic==2.4.0
`
    },
    {
      name: 'docker-compose.yml',
      type: 'file',
      content: `version: '3.8'

services:
  agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - API_KEY=\${API_KEY}
`
    },
    {
      name: 'deploy.yaml',
      type: 'file',
      content: `apiVersion: apps/v1
kind: Deployment
metadata:
  name: genai-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent
  template:
    metadata:
      labels:
        app: agent
    spec:
      containers:
      - name: agent
        image: agent:latest
        ports:
        - containerPort: 8000
`
    }
  ]
}

const FileTree = ({ node, level = 0, onSelect, selected }: { node: FileNode, level?: number, onSelect: (path: string, content?: string) => void, selected: string }) => {
  const [expanded, setExpanded] = useState(true)
  const path = node.name

  const isSelected = selected === path

  if (node.type === 'folder') {
    return (
      <div>
        <div
          className={`flex items-center space-x-2 py-1 px-2 rounded cursor-pointer hover:bg-[#1F1F1F] transition-colors ${
            isSelected ? 'bg-[#1F1F1F] border-l-2 border-accent' : ''
          }`}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? <ChevronDown className="w-4 h-4 text-text/70" /> : <ChevronRight className="w-4 h-4 text-text/70" />}
          <Folder className="w-4 h-4 text-accent" />
          <span className="text-sm text-text">{node.name}</span>
        </div>
        {expanded && node.children && (
          <div>
            {node.children.map((child, index) => (
              <FileTree key={index} node={child} level={level + 1} onSelect={onSelect} selected={selected} />
            ))}
          </div>
        )}
      </div>
    )
  }

  const iconMap: { [key: string]: any } = {
    'Dockerfile': Box,
    '.yml': Settings,
    '.yaml': Settings,
    '.py': FileCode,
    '.txt': File,
    '.json': File,
  }

  const Icon = Object.entries(iconMap).find(([key]) => path.includes(key))?.[1] || File

  return (
    <div
      className={`flex items-center space-x-2 py-1 px-2 rounded cursor-pointer hover:bg-[#1F1F1F] transition-colors ${
        isSelected ? 'bg-[#1F1F1F] border-l-2 border-accent' : ''
      }`}
      style={{ paddingLeft: `${level * 16 + 8}px` }}
      onClick={() => onSelect(path, node.content)}
    >
      <Icon className="w-4 h-4 text-secondary" />
      <span className="text-sm text-text">{node.name}</span>
    </div>
  )
}

export default function ExplorerPage() {
  const [selectedFile, setSelectedFile] = useState('')
  const [fileContent, setFileContent] = useState('')

  const handleSelect = (path: string, content?: string) => {
    setSelectedFile(path)
    setFileContent(content || '')
  }

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-heading font-bold mb-8">Project Explorer</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* File Tree */}
          <div className="lg:col-span-1 card">
            <h2 className="text-xl font-heading font-bold mb-4">Files</h2>
            <div className="overflow-y-auto max-h-[600px]">
              <FileTree node={projectFiles} onSelect={handleSelect} selected={selectedFile} />
            </div>
          </div>

          {/* Code Preview */}
          <div className="lg:col-span-2 card">
            <h2 className="text-xl font-heading font-bold mb-4">
              {selectedFile || 'Select a file to view'}
            </h2>
            {fileContent ? (
              <div className="bg-[#060606] border border-[#1F1F1F] rounded-lg p-4 overflow-x-auto">
                <pre className="text-sm font-mono text-text">
                  <code>{fileContent}</code>
                </pre>
              </div>
            ) : (
              <div className="bg-[#060606] border border-[#1F1F1F] rounded-lg p-8 text-center text-text/50">
                <FileCode className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No file selected. Click on a file in the tree to view its contents.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

