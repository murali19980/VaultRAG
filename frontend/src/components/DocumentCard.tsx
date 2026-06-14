"use client";

import { useState, useEffect } from "react";
import { FileText, Trash2, Loader2 } from "lucide-react";
import api from "@/lib/api";

interface DocumentCardProps {
  fileName: string;
  onDelete: () => void;
}

export default function DocumentCard({ fileName, onDelete }: DocumentCardProps) {
  const [deleting, setDeleting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [metadata, setMetadata] = useState<{ size_bytes: number; upload_date: string } | null>(null);

  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const res = await api.get(`/documents/${encodeURIComponent(fileName)}/metadata`);
        setMetadata(res.data);
      } catch (err) {
        console.error("Failed to fetch metadata for", fileName, err);
      }
    };
    fetchMetadata();
  }, [fileName]);

  const formatFileSize = (bytes?: number) => {
    if (bytes === undefined) return "Loading size...";
    const units = ["B", "KB", "MB", "GB"];
    let size = bytes;
    let unitIndex = 0;
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    return `${size.toFixed(1)} ${units[unitIndex]}`;
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return "Loading date...";
    return new Date(dateStr).toLocaleDateString();
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await api.delete(`/documents/${encodeURIComponent(fileName)}`);
      onDelete();
    } catch (err) {
      console.error("Delete failed", err);
    } finally {
      setDeleting(false);
      setShowConfirm(false);
    }
  };

  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100/70 dark:bg-gray-800/40 dark:hover:bg-gray-800/80 rounded-xl border border-gray-100 dark:border-gray-800/80 transition-all">
      <div className="flex items-center gap-3 overflow-hidden flex-1">
        <FileText className="w-5 h-5 text-blue-500 dark:text-blue-400 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-gray-900 dark:text-gray-100 truncate" title={fileName}>
            {fileName}
          </p>
          <p className="text-[10px] text-gray-400 dark:text-gray-500 font-medium">
            {metadata ? `${formatFileSize(metadata.size_bytes)} • ${formatDate(metadata.upload_date)}` : "Loading info..."}
          </p>
        </div>
      </div>

      {showConfirm ? (
        <div className="flex items-center gap-1.5 flex-shrink-0">
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="px-2 py-1 text-[10px] font-bold bg-red-600 hover:bg-red-700 text-white rounded-lg shadow-sm transition disabled:opacity-50"
          >
            {deleting ? <Loader2 className="w-3 h-3 animate-spin" /> : "Confirm"}
          </button>
          <button
            onClick={() => setShowConfirm(false)}
            className="px-2 py-1 text-[10px] font-bold bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition"
          >
            Cancel
          </button>
        </div>
      ) : (
        <button
          onClick={() => setShowConfirm(true)}
          className="p-1.5 text-gray-400 hover:text-red-600 dark:text-gray-500 dark:hover:text-red-400 rounded-lg transition flex-shrink-0"
          title="Delete document"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
