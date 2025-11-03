export type Stage = "uploaded" | "summarized" | "sentiment" | "routed";

export type Ticket = {
	id: number;
	text: string;
	summary?: string;
	sentiment?: string;
	urgency?: string;
	action?: string;
	stage: Stage;
	createdAt?: string;
	confidence?: string;
	keywords?: string[];
};

// Read endpoints from environment so they can point to deployed agents.
// Use NEXT_PUBLIC_* so the variables are exposed to client-side code.
export const AGENT_ENDPOINTS = {
  summarize: process.env.NEXT_PUBLIC_SUMMARIZE_URL ?? "/customer-support",
  sentiment: process.env.NEXT_PUBLIC_SENTIMENT_URL ?? "/sentiment",
  route: process.env.NEXT_PUBLIC_ROUTE_URL ?? "/content-writer",
};
