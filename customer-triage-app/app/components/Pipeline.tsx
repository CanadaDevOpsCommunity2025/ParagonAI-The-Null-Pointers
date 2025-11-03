"use client";
import React from "react";
import { Ticket, AGENT_ENDPOINTS } from "./types";

type Props = {
	ticket: Ticket;
};

const steps = [
	{ key: "content-writer", label: "Content Writer Agent", endpoint: AGENT_ENDPOINTS.summarize },
	{ key: "sentiment", label: "Sentiment Agent", endpoint: AGENT_ENDPOINTS.sentiment },
	{ key: "customer-support", label: "Customer Support Agent", endpoint: AGENT_ENDPOINTS.route },
];

export default function Pipeline({ ticket }: Props) {
	const { summary, sentiment, urgency, action, stage, confidence, keywords } = ticket;

	const renderOutput = (stepKey: string) => {
		if (stepKey === "summarized") {
			return summary ? (
				<div className="text-base text-gray-100 leading-relaxed font-medium">{summary}</div>
			) : (
				<div className="text-base text-gray-500 italic font-medium">Not processed yet</div>
			);
		}
		if (stepKey === "sentiment") {
			if (sentiment || urgency) {
				return (
					<div className="space-y-3">
						<div className="flex flex-wrap gap-2">
							{sentiment && (
								<span className="px-3 py-1.5 text-sm font-black rounded-lg bg-gray-700 text-white">
									{sentiment}
								</span>
							)}
							{urgency && (
								<span className={`px-3 py-1.5 text-sm font-black rounded-lg ${
									urgency.includes('critical') ? 'bg-gradient-to-r from-red-500 to-red-600 text-white shadow-lg shadow-red-500/50' :
									urgency.includes('high') ? 'bg-gradient-to-r from-amber-500 to-yellow-600 text-black shadow-lg shadow-amber-500/50' :
									urgency.includes('medium') ? 'bg-gray-600 text-white' :
									'bg-gray-700 text-white'
								}`}>
									{urgency}
								</span>
							)}
							{confidence && (
								<span className="px-3 py-1.5 text-xs font-black rounded-lg bg-blue-600/20 text-blue-300 border border-blue-500/30">
									⚡ Confidence: {confidence}
								</span>
							)}
						</div>
						{keywords && keywords.length > 0 && (
							<div className="mt-2">
								<div className="text-xs font-bold text-gray-400 mb-1.5">🏷️ Keywords Detected:</div>
								<div className="flex flex-wrap gap-1.5">
									{keywords.map((keyword, idx) => (
										<span key={idx} className="px-2 py-1 text-xs font-semibold rounded-md bg-gray-800/50 text-gray-300 border border-gray-700/50">
											{keyword}
										</span>
									))}
								</div>
							</div>
						)}
					</div>
				);
			}
			return <div className="text-base text-gray-500 italic font-medium">Not processed yet</div>;
		}
		if (stepKey === "routed") {
			return action ? (
				<div className="text-base font-black text-white">{action}</div>
			) : (
				<div className="text-base text-gray-500 italic font-medium">Not processed yet</div>
			);
		}
		return null;
	};

	return (
		<div className="space-y-6">
			{/* Progress Steps */}
			<div className="flex items-center justify-between relative">
				<div className="absolute top-6 left-0 right-0 h-1 bg-gradient-to-r from-gray-700 via-gray-600 to-gray-700 rounded-full" />
				{steps.map((s, idx) => {
					const done =
						s.key === "summarized" ? !!summary : s.key === "sentiment" ? !!sentiment || !!urgency : !!action;
					const isCurrent = stage === s.key;
					return (
						<div key={s.key} className="flex flex-col items-center gap-3 relative z-10">
							<div
								className={`w-12 h-12 rounded-2xl flex items-center justify-center text-lg font-black transition-all shadow-xl ${
									done
										? "bg-gradient-to-br from-amber-500 to-yellow-600 text-black shadow-amber-500/50"
										: isCurrent
										? "bg-gradient-to-br from-gray-700 to-gray-600 text-amber-400 animate-pulse shadow-amber-500/30"
										: "bg-gray-800 text-gray-500 border-2 border-gray-700"
								}`}
							>
								{done ? (
									<svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
										<path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
									</svg>
								) : (
									<svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										{s.key === "summarized" ? (
											<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
										) : s.key === "sentiment" ? (
											<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
										) : (
											<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
										)}
									</svg>
								)}
							</div>
							<div className="text-center">
								<div className="text-sm font-black text-white">{s.label}</div>
							</div>
						</div>
					);
				})}
			</div>

			{/* Step Outputs */}
			<div className="space-y-4">
				{steps.map((s) => (
					<div key={s.key} className="bg-black/30 backdrop-blur rounded-2xl p-4 border border-gray-700/50">
						<div className="flex items-center gap-3 mb-3">
							<svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								{s.key === "summarized" ? (
									<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
								) : s.key === "sentiment" ? (
									<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
								) : (
									<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
								)}
							</svg>
							<div className="text-sm font-black text-gray-300 uppercase tracking-wider">{s.label}</div>
						</div>
						{renderOutput(s.key)}
						<div className="text-[10px] text-gray-600 mt-3 font-mono">{s.endpoint}</div>
					</div>
				))}
			</div>
		</div>
	);
}
