"use client";
import React, { useState, useEffect } from "react";
import { useChat } from "@/hooks/useChat";
import { useSessions } from "@/hooks/useSessions";
import SessionSidebar from "@/components/SessionSidebar";
import ChatInput from "@/components/ChatInput";
import TypingIndicator from "@/components/TypingIndicator";
import CitationBadge from "@/components/CitationBadge";
import { Shield, Sparkles, Database, ArrowRight } from "lucide-react";

export default function Home() {
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const { sessions, createSession } = useSessions();
  const { messages, loading, sendMessage, loadMessages } = useChat(currentSessionId);

  // Load active session messages
  useEffect(() => {
    loadMessages(currentSessionId);
  }, [currentSessionId, loadMessages]);

  const handleNewSession = async () => {
    // Generate a default title with the current date/time
    const title = `Chat Session ${new Date().toLocaleDateString()}`;
    const newId = await createSession(title);
    setCurrentSessionId(newId);
  };

  return (
    <div className="flex h-screen bg-gray-50 text-gray-900 font-sans antialiased overflow-hidden">
      {/* Sessions & Document Sidebar */}
      <SessionSidebar
        currentSessionId={currentSessionId}
        onSelectSession={setCurrentSessionId}
        onNewSession={handleNewSession}
      />

      {/* Main Chat Workspace */}
      <div className="flex-1 flex flex-col h-full bg-slate-50 relative">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-md border-b border-gray-100 px-6 py-4 flex items-center justify-between z-10 shadow-sm">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse"></span>
            <h1 className="text-base font-semibold text-gray-800 flex items-center gap-1.5">
              <Shield size={16} className="text-blue-600" /> VaultRAG Enterprise Workspace
            </h1>
          </div>
          <div className="text-xs text-gray-400 bg-gray-100 px-2.5 py-1 rounded-full font-medium">
            Local Air-Gapped Mode
          </div>
        </header>

        {/* Chat History Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
          {!currentSessionId ? (
            /* Welcome / Empty State Screen */
            <div className="max-w-xl mx-auto mt-16 text-center space-y-8 animate-fade-in">
              <div className="space-y-3">
                <div className="inline-flex items-center justify-center p-3.5 bg-blue-50 text-blue-600 rounded-2xl shadow-inner mb-2">
                  <Database size={32} />
                </div>
                <h2 className="text-2xl font-bold text-gray-800 tracking-tight">
                  Welcome to VaultRAG
                </h2>
                <p className="text-sm text-gray-500 leading-relaxed max-w-md mx-auto">
                  A secure sandbox for your company's files. Upload documents to the Document Vault in the sidebar and query them with absolute privacy.
                </p>
              </div>

              {/* Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
                <div className="p-4 bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                  <h3 className="text-xs font-bold text-blue-600 uppercase tracking-wider flex items-center gap-1.5 mb-1.5">
                    <Sparkles size={13} /> Hybrid Search RAG
                  </h3>
                  <p className="text-xs text-gray-500 leading-normal">
                    Combines vector embeddings with BM25 keyword matching using Reciprocal Rank Fusion (RRF) for top accuracy.
                  </p>
                </div>
                <div className="p-4 bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                  <h3 className="text-xs font-bold text-blue-600 uppercase tracking-wider flex items-center gap-1.5 mb-1.5">
                    <Shield size={13} /> Strict Privacy
                  </h3>
                  <p className="text-xs text-gray-500 leading-normal">
                    Designed to work completely offline. Your queries, chats, and files never leave your infrastructure.
                  </p>
                </div>
              </div>

              {/* Get Started Button */}
              <div>
                <button
                  onClick={handleNewSession}
                  className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl py-3 px-6 font-semibold text-sm shadow-lg hover:shadow-blue-500/20 active:scale-95 transition-all"
                >
                  Start Chat Session <ArrowRight size={16} />
                </button>
              </div>
            </div>
          ) : (
            /* Message Bubbles */
            <>
              {messages.length === 0 && (
                <div className="text-center py-20 text-sm text-gray-400">
                  Ask a question to search your document repository...
                </div>
              )}
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-slide-up`}
                >
                  <div
                    className={`max-w-2xl rounded-2xl px-4.5 py-3 shadow-sm border ${
                      msg.role === "user"
                        ? "bg-blue-600 text-white border-blue-500 rounded-br-sm"
                        : "bg-white text-gray-800 border-gray-100 rounded-bl-sm"
                    }`}
                  >
                    <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-3 pt-2.5 border-t border-gray-100 flex flex-wrap gap-2">
                        {msg.citations.map((c, i) => (
                          <CitationBadge key={i} citation={c} />
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start animate-pulse">
                  <TypingIndicator />
                </div>
              )}
            </>
          )}
        </div>

        {/* Input Bar */}
        <ChatInput onSend={sendMessage} disabled={loading || !currentSessionId} />
      </div>
    </div>
  );
}
