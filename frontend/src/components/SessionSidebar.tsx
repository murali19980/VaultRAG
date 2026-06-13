import React, { useState, useEffect, useCallback } from "react";
import { useSessions } from "@/hooks/useSessions";
import { MessageSquare, Plus, Trash2, Database, X, FileText } from "lucide-react";
import api from "@/lib/api";
import FileUploader from "./FileUploader";

interface Props {
  currentSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
}

export default function SessionSidebar({ currentSessionId, onSelectSession, onNewSession }: Props) {
  const { sessions, deleteSession, refreshSessions } = useSessions();
  const [showDocs, setShowDocs] = useState(false);
  const [docsRefreshCounter, setDocsRefreshCounter] = useState(0);
  const [pendingDocs, setPendingDocs] = useState<string[]>([]);

  const handleUploadComplete = (filenames: string[]) => {
    // Add uploaded files to pending tracking state
    setPendingDocs(prev => [...prev, ...filenames]);
    setDocsRefreshCounter(prev => prev + 1);
  };

  return (
    <div className="w-64 bg-gray-950 text-gray-100 flex flex-col h-full border-r border-gray-800 shadow-2xl">
      {/* Header / New Chat */}
      <div className="p-4 border-b border-gray-800">
        <button
          onClick={onNewSession}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-lg py-2.5 px-4 flex items-center justify-center gap-2 font-medium text-sm transition-all shadow-md active:scale-95 animate-fade-in"
        >
          <Plus size={16} /> New Chat
        </button>
      </div>

      {/* Sessions History List */}
      <div className="flex-1 overflow-y-auto py-2">
        <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
          Recent Chats
        </div>
        {sessions.length === 0 ? (
          <div className="px-4 py-3 text-xs text-gray-600 italic">No recent chats</div>
        ) : (
          sessions.map(s => (
            <div
              key={s.id}
              className={`flex items-center justify-between mx-2 px-3 py-2.5 rounded-lg cursor-pointer transition-all group ${
                currentSessionId === s.id
                  ? "bg-gray-800 text-white shadow-inner font-medium"
                  : "text-gray-400 hover:bg-gray-900 hover:text-gray-200"
              }`}
              onClick={() => onSelectSession(s.id)}
            >
              <div className="flex items-center gap-2 truncate flex-1 mr-2">
                <MessageSquare size={14} className={currentSessionId === s.id ? "text-blue-400" : "text-gray-500"} />
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
      <div className="border-t border-gray-800 bg-gray-900/50">
        <button
          onClick={() => setShowDocs(!showDocs)}
          className="w-full flex items-center justify-between px-4 py-3 text-xs font-semibold text-gray-400 hover:bg-gray-900 transition-all uppercase tracking-wider"
        >
          <span className="flex items-center gap-1.5"><Database size={12} /> Document Vault</span>
          <span>{showDocs ? "▼" : "▲"}</span>
        </button>
        
        {showDocs && (
          <div className="px-4 pb-4 space-y-3">
            <div className="pt-1">
              <FileUploader onUploadComplete={handleUploadComplete} />
            </div>
            <DocumentList
              refreshCounter={docsRefreshCounter}
              pendingDocs={pendingDocs}
              setPendingDocs={setPendingDocs}
            />
          </div>
        )}
      </div>
    </div>
  );
}

function DocumentList({
  refreshCounter,
  pendingDocs,
  setPendingDocs
}: {
  refreshCounter: number;
  pendingDocs: string[];
  setPendingDocs: React.Dispatch<React.SetStateAction<string[]>>;
}) {
  const [docs, setDocs] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchDocs = useCallback(async () => {
    try {
      const res = await api.get("/documents");
      const fetchedDocs = res.data.documents || [];
      setDocs(fetchedDocs);
      
      // Remove any pending docs that are now indexed (in fetched list)
      if (pendingDocs.length > 0) {
        const stillPending = pendingDocs.filter(p => !fetchedDocs.includes(p));
        if (stillPending.length !== pendingDocs.length) {
          setPendingDocs(stillPending);
        }
      }
    } catch (err) {
      console.error("Failed to fetch documents", err);
    }
  }, [pendingDocs, setPendingDocs]);

  // Fetch when manual refresh triggered
  useEffect(() => {
    setLoading(true);
    fetchDocs().finally(() => setLoading(false));
  }, [refreshCounter, fetchDocs]);

  // Set up background polling only when there are files actively indexing
  useEffect(() => {
    if (pendingDocs.length === 0) return;

    const interval = setInterval(() => {
      fetchDocs();
    }, 3000); // Check database every 3 seconds

    return () => clearInterval(interval);
  }, [pendingDocs, fetchDocs]);

  const deleteDoc = async (name: string) => {
    try {
      await api.delete(`/documents/${encodeURIComponent(name)}`);
      fetchDocs();
    } catch (err) {
      console.error("Failed to delete document", err);
    }
  };

  if (loading && docs.length === 0 && pendingDocs.length === 0) {
    return <div className="text-gray-600 text-xs italic">Loading database...</div>;
  }

  return (
    <div className="space-y-1.5 max-h-40 overflow-y-auto text-xs scrollbar-thin">
      {/* Pending (Indexing) Documents */}
      {pendingDocs.map(p => (
        <div key={`pending-${p}`} className="flex justify-between items-center bg-gray-900/60 p-1.5 rounded border border-blue-900/40 animate-pulse">
          <span className="truncate text-blue-400 flex items-center gap-1.5 max-w-[85%]">
            <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-ping shrink-0" />
            <span className="truncate" title={p}>{p}</span>
            <span className="text-[10px] text-blue-500/70 italic shrink-0 font-medium">(indexing...)</span>
          </span>
        </div>
      ))}

      {/* Completed/Indexed Documents */}
      {docs.length === 0 && pendingDocs.length === 0 ? (
        <div className="text-gray-600 italic py-1">No documents indexed</div>
      ) : (
        docs.map(d => (
          <div key={d} className="flex justify-between items-center bg-gray-900 p-1.5 rounded border border-gray-800/80 group">
            <span className="truncate text-gray-400 flex items-center gap-1.5 max-w-[80%]">
              <FileText size={10} className="text-gray-500 shrink-0" />
              <span className="truncate" title={d}>{d}</span>
            </span>
            <button
              onClick={() => deleteDoc(d)}
              className="text-gray-600 hover:text-red-400 p-0.5 rounded transition-all"
              title="Delete Document from Vault"
            >
              <X size={12} />
            </button>
          </div>
        ))
      )}
    </div>
  );
}