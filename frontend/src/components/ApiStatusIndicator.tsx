"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";
import { Server, Activity, ShieldAlert, Cpu } from "lucide-react";

interface HealthDetailed {
  status: string;
  models: {
    embedding: string;
    chat: string;
  };
  vram_usage_mb?: number;
  last_query_latency?: {
    retrieval_ms: number;
    synthesis_ms: number;
    total_ms: number;
    query: string;
  };
  ollama_status: "running" | "unreachable";
}

export default function ApiStatusIndicator() {
  const [health, setHealth] = useState<HealthDetailed | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const fetchStatus = async () => {
    try {
      const res = await api.get("/health/detailed");
      setHealth(res.data);
      setError(false);
    } catch (err) {
      console.error("Health check failed", err);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    if (error) return "bg-red-500";
    if (!health) return "bg-yellow-500";
    if (health.ollama_status === "running") return "bg-green-500";
    return "bg-yellow-500";
  };

  const getStatusText = () => {
    if (error) return "Backend unreachable";
    if (!health) return "Loading...";
    if (health.ollama_status === "running") return "All systems operational";
    return "Ollama not responding";
  };

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition"
      >
        <div className={`w-2.5 h-2.5 rounded-full ${getStatusColor()} animate-pulse`} />
        <span className="text-xs font-semibold text-gray-700 dark:text-gray-300">
          {loading ? "Checking..." : getStatusText()}
        </span>
      </button>

      {/* Modal with detailed status */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in" onClick={() => setShowModal(false)}>
          <div className="bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-2xl shadow-xl max-w-md w-full mx-4 p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-bold text-gray-950 dark:text-gray-50 flex items-center gap-2">
                <Server className="w-5 h-5 text-blue-600 dark:text-blue-400" /> System Status Dashboard
              </h2>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300">✕</button>
            </div>

            {health ? (
              <div className="space-y-4 text-sm text-gray-700 dark:text-gray-300">
                <div className="flex justify-between pb-2 border-b border-gray-100 dark:border-gray-800">
                  <span className="font-semibold text-gray-900 dark:text-gray-200">Backend Server:</span>
                  <span className="text-green-600 dark:text-green-400 font-bold flex items-center gap-1">Online</span>
                </div>
                <div className="flex justify-between pb-2 border-b border-gray-100 dark:border-gray-800">
                  <span className="font-semibold text-gray-900 dark:text-gray-200">Ollama API Status:</span>
                  <span className={`font-bold ${health.ollama_status === "running" ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>
                    {health.ollama_status === "running" ? "Running" : "Unreachable"}
                  </span>
                </div>
                <div className="flex justify-between pb-2 border-b border-gray-100 dark:border-gray-800">
                  <span className="font-semibold text-gray-900 dark:text-gray-200">Embedding Model:</span>
                  <span className="font-mono text-xs text-gray-500 dark:text-gray-400">{health.models?.embedding || "N/A"}</span>
                </div>
                <div className="flex justify-between pb-2 border-b border-gray-100 dark:border-gray-800">
                  <span className="font-semibold text-gray-900 dark:text-gray-200">Chat Language Model:</span>
                  <span className="font-mono text-xs text-gray-500 dark:text-gray-400">{health.models?.chat || "N/A"}</span>
                </div>
                {health.vram_usage_mb !== null && health.vram_usage_mb !== undefined && (
                  <div className="flex justify-between pb-2 border-b border-gray-100 dark:border-gray-800">
                    <span className="font-semibold text-gray-900 dark:text-gray-200 flex items-center gap-1">
                      <Cpu className="w-4 h-4 text-emerald-500" /> GPU VRAM Usage:
                    </span>
                    <span className="font-mono">{health.vram_usage_mb} MiB</span>
                  </div>
                )}
                {health.last_query_latency ? (
                  <div className="border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/40 rounded-xl p-3.5 mt-4">
                    <div className="font-semibold text-gray-950 dark:text-gray-100 mb-2 flex items-center gap-1.5">
                      <Activity className="w-4 h-4 text-blue-500" /> Last Query Latency (Sec)
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <span className="text-gray-500">Retrieval:</span>
                      <span className="font-mono font-medium text-right text-gray-900 dark:text-gray-200">{(health.last_query_latency.retrieval_ms / 1000).toFixed(3)}s</span>
                      <span className="text-gray-500">Synthesis:</span>
                      <span className="font-mono font-medium text-right text-gray-900 dark:text-gray-200">{(health.last_query_latency.synthesis_ms / 1000).toFixed(3)}s</span>
                      <span className="text-gray-900 dark:text-gray-100 font-bold border-t border-gray-200 dark:border-gray-700 pt-1 mt-1">Total:</span>
                      <span className="font-mono font-bold text-right text-gray-950 dark:text-gray-50 border-t border-gray-200 dark:border-gray-700 pt-1 mt-1">{(health.last_query_latency.total_ms / 1000).toFixed(3)}s</span>
                    </div>
                    <div className="mt-2.5 pt-2 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-500 dark:text-gray-400 italic truncate" title={health.last_query_latency.query}>
                      "{health.last_query_latency.query}"
                    </div>
                  </div>
                ) : (
                  <div className="border border-dashed border-gray-200 dark:border-gray-800 rounded-xl p-4 mt-4 text-center text-xs text-gray-400">
                    No query performance metrics collected yet.
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-6">
                <ShieldAlert className="w-10 h-10 text-red-500 mx-auto mb-2" />
                <p className="text-red-600 dark:text-red-400 font-medium">Failed to connect to the backend health endpoint.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
