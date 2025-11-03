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
    const s = text.replace(/\s+/g, " ").trim();
    if (s.length > 120) return s.slice(0, 120) + "...";
    return s;
  };

  const analyzeSentiment = async (summary: string) => {
    const lower = summary.toLowerCase();
    if (/(can't|cannot|not|fail|error|unable|broken|refund|angry|threaten)/.test(lower)) {
      if (/(threaten|move to another provider|i'll move|i will move)/.test(lower))
        return { sentiment: "angry", urgency: "critical" };
      if (/(can't|cannot|unable|fail|error)/.test(lower)) return { sentiment: "frustrated", urgency: "high" };
      return { sentiment: "negative", urgency: "high" };
    }
    if (/(thanks|thank you|good|safe|arrived)/.test(lower)) return { sentiment: "neutral", urgency: "low" };
    return { sentiment: "neutral", urgency: "medium" };
  };

  const routeDecision = async ({ urgency, sentiment }: { urgency?: string; sentiment?: string }) => {
    if (urgency === "critical" || urgency === "high" || sentiment === "angry") return "escalate_to_human";
    return "normal_queue";
  };

  const runPipeline = async (id: number, ticketOverride?: Ticket) => {
    const ticket = ticketOverride || tickets.find((t) => t.id === id);
    if (!ticket) return;
    updateTicket(id, { stage: "summarized" });
    const summary = await summarize(ticket.text);
    updateTicket(id, { summary });
    updateTicket(id, { stage: "sentiment" });
    const sent = await analyzeSentiment(summary);
    updateTicket(id, { sentiment: sent.sentiment, urgency: sent.urgency });
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
