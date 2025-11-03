"use client";
import React, { useState } from "react";

type Props = {
  onAdd: (text: string) => void;
};

export default function TicketUploader({ onAdd }: Props) {
  const [text, setText] = useState("");

  return (
    <div className="relative bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-3xl shadow-2xl border border-gray-700/50 p-8 overflow-hidden">
      <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-amber-500/10 to-transparent rounded-full blur-3xl"></div>
      
      <div className="relative">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 bg-gradient-to-br from-amber-500 to-yellow-600 rounded-2xl flex items-center justify-center shadow-lg shadow-amber-500/50">
            <svg className="w-6 h-6 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 4v16m8-8H4" />
            </svg>
          </div>
          <h3 className="text-2xl font-black text-white">New Ticket</h3>
        </div>
        
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste customer ticket text here..."
          className="w-full p-5 border-2 border-gray-600/50 rounded-2xl focus:ring-4 focus:ring-amber-500/50 focus:border-amber-500 transition-all bg-black/50 backdrop-blur text-white placeholder-gray-500 resize-none font-semibold text-base leading-relaxed"
          rows={7}
        />
        
        <button
          className="group mt-6 w-full bg-gradient-to-r from-amber-500 via-yellow-500 to-amber-600 hover:from-amber-400 hover:via-yellow-400 hover:to-amber-500 text-black font-black py-4 px-6 rounded-2xl shadow-xl shadow-amber-500/40 hover:shadow-2xl hover:shadow-amber-400/50 transition-all duration-300 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:shadow-amber-500/40 transform hover:scale-[1.02] overflow-hidden"
          onClick={() => {
            if (!text.trim()) return;
            onAdd(text.trim());
            setText("");
          }}
          disabled={!text.trim()}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
          <div className="relative flex items-center justify-center gap-3">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 4v16m8-8H4" />
            </svg>
            <span className="text-lg tracking-wide">Add & Process Ticket</span>
          </div>
        </button>
      </div>
    </div>
  );
}
