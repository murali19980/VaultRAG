"use client";

import React from "react";
import Link from "next/link";
import { useSessions } from "@/hooks/useSessions";
import { MessageSquare, Plus, Trash2, Database } from "lucide-react";

interface Props {
  currentSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
}

export default function SessionSidebar({ currentSessionId, onSelectSession, onNewSession }: Props) {
  const { sessions, deleteSession } = useSessions();

  return (
    <div className="w-64 bg-gray-955 dark:bg-gray-950 text-gray-100 flex flex-col h-full border-r border-gray-800 dark:border-gray-900 shadow-2xl transition-colors">
      {/* Header / New Chat */}
      <div className="p-4 border-b border-gray-800 dark:border-gray-900">
        <button
          onClick={onNewSession}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-lg py-2.5 px-4 flex items-center justify-center gap-2 font-medium text-sm transition-all shadow-md active:scale-95 animate-fade-in"
        >
          <Plus size={16} /> New Chat
        </button>
      </div>

      {/* Sessions History List */}
      <div className="flex-1 overflow-y-auto py-2">
        <div className="px-4 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
          Recent Chats
        </div>
        {sessions.length === 0 ? (
          <div className="px-4 py-3 text-xs text-gray-650 italic">No recent chats</div>
        ) : (
          sessions.map(s => (
            <div
              key={s.id}
              className={`flex items-center justify-between mx-2 px-3 py-2.5 rounded-lg cursor-pointer transition-all group ${
                currentSessionId === s.id
                  ? "bg-gray-800 dark:bg-gray-800/80 text-white shadow-inner font-medium"
                  : "text-gray-400 hover:bg-gray-900 dark:hover:bg-gray-900/60 hover:text-gray-200"
              }`}
              onClick={() => onSelectSession(s.id)}
            >
              <div className="flex items-center gap-2 truncate flex-1 mr-2">
                <MessageSquare size={14} className={currentSessionId === s.id ? "text-blue-400" : "text-gray-505"} />
                <span className="truncate text-xs">{s.title}</span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteSession(s.id);
                  if (currentSessionId === s.id) {
                    onSelectSession("");
                  }
                }}
                className="text-gray-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity p-0.5"
                title="Delete Session"
              >
                <Trash2 size={13} />
              </button>
            </div>
          ))
        )}
      </div>

      {/* Document Manager Section */}
      <div className="border-t border-gray-800 dark:border-gray-900 p-4 bg-gray-900/50">
        <Link
          href="/documents"
          className="w-full border border-gray-800 dark:border-gray-800/60 hover:bg-gray-800 text-gray-300 hover:text-white rounded-lg py-2.5 px-4 flex items-center justify-center gap-2 font-medium text-xs transition-all active:scale-95"
        >
          <Database size={14} /> Manage Document Vault
        </Link>
      </div>
    </div>
  );
}