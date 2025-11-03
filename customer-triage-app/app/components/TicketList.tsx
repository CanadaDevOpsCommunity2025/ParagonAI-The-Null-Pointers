"use client";
import React from "react";
import { Ticket } from "./types";
import Pipeline from "./Pipeline";

type Props = {
	tickets: Ticket[];
	onRun: (id: number) => void;
};

export default function TicketList({ tickets, onRun }: Props) {
	if (!tickets || tickets.length === 0) {
		return (
			<div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-3xl shadow-2xl border border-gray-700/50 p-16 text-center">
				<div className="w-24 h-24 bg-gradient-to-br from-gray-800 to-gray-700 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-xl">
					<svg className="w-12 h-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
					</svg>
				</div>
				<h3 className="text-2xl font-black text-white mb-3">No tickets yet</h3>
				<p className="text-gray-400 font-semibold text-lg">Add a new ticket to get started</p>
			</div>
		);
	}

	return (
		<div className="space-y-6">
			{tickets.map((t) => (
				<div
					key={t.id}
					className={`relative bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-3xl shadow-2xl border-2 transition-all duration-300 hover:shadow-amber-500/20 ${
						t.action === "escalate_to_human" 
							? "border-amber-500/60 shadow-amber-500/30" 
							: "border-gray-700/50 hover:border-gray-600"
					}`}
				>
					{t.action === "escalate_to_human" && (
						<div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-amber-500/10 to-transparent rounded-full blur-3xl"></div>
					)}
					
					<div className="relative p-8">
						<div className="flex items-start justify-between mb-6">
							<div className="flex items-center gap-4">
								<div className="w-16 h-16 bg-gradient-to-br from-gray-800 to-gray-700 rounded-2xl flex items-center justify-center shadow-xl">
									<span className="text-2xl font-black bg-gradient-to-br from-amber-400 to-yellow-600 bg-clip-text text-transparent">#{t.id}</span>
								</div>
								<div>
									<div className="text-xs font-black text-gray-400 uppercase tracking-widest mb-1">Ticket</div>
									<div className="text-lg font-black text-gray-200">Stage: <span className="text-white">{t.stage}</span></div>
								</div>
							</div>
							<div className="flex items-center gap-3">
								{t.action === "escalate_to_human" ? (
									<span className="px-4 py-2 text-sm font-black rounded-xl bg-gradient-to-r from-amber-500 to-yellow-600 text-black shadow-lg shadow-amber-500/50 flex items-center gap-2">
										<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
											<path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
										</svg>
										ESCALATE
									</span>
								) : t.action ? (
									<span className="px-4 py-2 text-sm font-black rounded-xl bg-gray-700/80 text-white shadow-lg flex items-center gap-2">
										<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
											<path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
										</svg>
										NORMAL
									</span>
								) : null}
								<button
									onClick={() => onRun(t.id)}
									className="px-5 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-600 hover:from-amber-400 hover:to-yellow-500 text-black text-sm font-black rounded-xl transition-all shadow-lg shadow-amber-500/50 hover:shadow-xl hover:shadow-amber-400/60 transform hover:scale-105"
								>
									<div className="flex items-center gap-2">
										<svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
											<path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
										</svg>
										Run
									</div>
								</button>
							</div>
						</div>

						<div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
							<div className="space-y-3">
								<div className="text-sm font-black text-gray-400 uppercase tracking-widest flex items-center gap-2">
									<div className="w-1 h-4 bg-gradient-to-b from-amber-500 to-yellow-600 rounded-full"></div>
									Original Message
								</div>
								<div className="p-6 bg-black/50 backdrop-blur rounded-2xl border border-gray-700/50">
									<div className="whitespace-pre-wrap text-base text-gray-100 leading-relaxed font-medium">{t.text}</div>
								</div>
							</div>

							<div>
								<div className="text-sm font-black text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-2">
									<div className="w-1 h-4 bg-gradient-to-b from-amber-500 to-yellow-600 rounded-full"></div>
									AI Pipeline
								</div>
								<Pipeline ticket={t} />
							</div>
						</div>
					</div>
				</div>
			))}
		</div>
	);
}
