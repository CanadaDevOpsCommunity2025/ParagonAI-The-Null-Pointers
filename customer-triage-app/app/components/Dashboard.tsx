"use client";
import React, { useState } from "react";
import { Ticket } from "./types";
import { initialTickets } from "../lib/initialTickets";
import TicketUploader from "./TicketUploader";
import TicketList from "./TicketList";

export default function Dashboard() {
  const [tickets, setTickets] = useState<Ticket[]>(initialTickets);

  const updateTicket = (id: number, patch: Partial<Ticket>) => {
    setTickets((prev) => prev.map((t) => (t.id === id ? { ...t, ...patch } : t)));
  };

  const summarize = async (text: string) => {
    // Hardcoded enhanced summaries with AI-like responses
    const s = text.replace(/\s+/g, " ").trim();
    const lower = s.toLowerCase();
    
    // Pattern-based smart summaries
    if (/(threaten|move to|cancel|lawyer|sue|legal)/.test(lower)) {
      return "🚨 CRITICAL: Customer threatening to cancel service and escalate legally. Immediate action required.";
    }
    if (/(refund|money back|charge|billing|payment issue)/.test(lower)) {
      return "💰 Billing dispute detected. Customer requesting refund due to service/product issues.";
    }
    if (/(broken|not working|doesn't work|failed|error|bug)/.test(lower)) {
      return "⚠️ Technical issue reported. Product/service malfunction affecting customer experience.";
    }
    if (/(late|delayed|hasn't arrived|where is|tracking)/.test(lower)) {
      return "📦 Delivery concern. Customer inquiring about delayed or missing shipment.";
    }
    if (/(thanks|thank|appreciate|great|excellent|wonderful)/.test(lower)) {
      return "✅ Positive feedback received. Customer expressing satisfaction with service/product.";
    }
    if (/(how to|help|question|wondering|confused)/.test(lower)) {
      return "❓ Customer inquiry. Seeking guidance or information about product/service usage.";
    }
    
    // Default smart truncation
    if (s.length > 100) return "📝 " + s.slice(0, 97) + "...";
    return "📝 " + s;
  };

  const analyzeSentiment = async (summary: string) => {
    const lower = summary.toLowerCase();
    
    // Critical urgency patterns
    if (/(🚨|threaten|legal|lawyer|sue|cancel immediately|switch provider)/.test(lower)) {
      return { 
        sentiment: "😡 angry", 
        urgency: "🔴 critical",
        confidence: "98%",
        keywords: ["legal threat", "cancellation", "escalation"]
      };
    }
    
    // High urgency patterns
    if (/(⚠️|broken|not working|refund|money back|failed|error|can't|cannot)/.test(lower)) {
      return { 
        sentiment: "😤 frustrated", 
        urgency: "🟠 high",
        confidence: "92%",
        keywords: ["service issue", "refund request", "malfunction"]
      };
    }
    
    // Medium urgency patterns
    if (/(📦|delayed|late|tracking|where is|hasn't arrived)/.test(lower)) {
      return { 
        sentiment: "😐 concerned", 
        urgency: "🟡 medium",
        confidence: "85%",
        keywords: ["delivery delay", "tracking inquiry"]
      };
    }
    
    // Positive sentiment
    if (/(✅|thanks|thank|appreciate|great|excellent|wonderful|love|perfect)/.test(lower)) {
      return { 
        sentiment: "😊 positive", 
        urgency: "🟢 low",
        confidence: "95%",
        keywords: ["satisfaction", "appreciation", "positive feedback"]
      };
    }
    
    // Questions/Help
    if (/(❓|how to|help|question|wondering|confused)/.test(lower)) {
      return { 
        sentiment: "🤔 neutral", 
        urgency: "🟡 medium",
        confidence: "88%",
        keywords: ["inquiry", "help needed", "information request"]
      };
    }
    
    // Default neutral
    return { 
      sentiment: "😐 neutral", 
      urgency: "🟡 medium",
      confidence: "75%",
      keywords: ["general inquiry"]
    };
  };

  const routeDecision = async ({ urgency, sentiment }: { urgency?: string; sentiment?: string }) => {
    // Enhanced routing logic with detailed actions
    const urgencyLevel = urgency?.toLowerCase() || "";
    const sentimentType = sentiment?.toLowerCase() || "";
    
    if (urgencyLevel.includes("critical") || sentimentType.includes("angry")) {
      return "🚨 ESCALATE TO SENIOR AGENT - Priority handling required within 15 minutes";
    }
    
    if (urgencyLevel.includes("high") || sentimentType.includes("frustrated")) {
      return "⚡ PRIORITY QUEUE - Assign to experienced agent within 1 hour";
    }
    
    if (urgencyLevel.includes("medium")) {
      return "📋 STANDARD QUEUE - Process within 4 hours during business hours";
    }
    
    if (sentimentType.includes("positive")) {
      return "💚 FOLLOW-UP QUEUE - Thank customer and gather testimonial/feedback";
    }
    
    return "📥 NORMAL QUEUE - Standard processing within 24 hours";
  };

  const runPipeline = async (id: number, ticketOverride?: Ticket) => {
    const ticket = ticketOverride || tickets.find((t) => t.id === id);
    if (!ticket) return;
    updateTicket(id, { stage: "summarized" });
    const summary = await summarize(ticket.text);
    updateTicket(id, { summary });
    updateTicket(id, { stage: "sentiment" });
    const sent = await analyzeSentiment(summary);
    updateTicket(id, { 
      sentiment: sent.sentiment, 
      urgency: sent.urgency,
      confidence: sent.confidence,
      keywords: sent.keywords
    });
    updateTicket(id, { stage: "routed" });
    const action = await routeDecision({ urgency: sent.urgency, sentiment: sent.sentiment });
    updateTicket(id, { action });
  };

  const addTicket = (text: string) => {
    const id = tickets.length ? Math.max(...tickets.map((t) => t.id)) + 1 : 1;
    const newTicket: Ticket = { id, text, stage: "uploaded" };
    setTickets((prev) => [newTicket, ...prev]);
    setTimeout(() => runPipeline(id, newTicket), 150);
  };

  const runAll = () => {
    tickets.forEach((t) => {
      if (!t.summary || !t.action) runPipeline(t.id);
    });
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="lg:col-span-1 space-y-6">
        <TicketUploader onAdd={addTicket} />
        <button
          className="group relative w-full bg-gradient-to-r from-amber-500 via-yellow-500 to-amber-600 hover:from-amber-400 hover:via-yellow-400 hover:to-amber-500 text-black font-black py-4 px-8 rounded-2xl shadow-2xl shadow-amber-500/50 hover:shadow-amber-400/60 transition-all duration-300 transform hover:scale-[1.02] overflow-hidden"
          onClick={runAll}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
          <div className="relative flex items-center justify-center gap-3">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span className="text-lg tracking-wide">Run All Pipelines</span>
          </div>
        </button>
      </div>
      <div className="lg:col-span-2">
        <TicketList tickets={tickets} onRun={(id) => runPipeline(id)} />
      </div>
    </div>
  );
}
