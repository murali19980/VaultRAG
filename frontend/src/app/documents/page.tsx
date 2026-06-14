"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import api from "@/lib/api";
import { ArrowLeft, Upload, FolderPlus, FileText, Trash2, Edit2, Search, Folder, FolderOpen, Loader2 } from "lucide-react";
import DocumentCard from "@/components/DocumentCard";

interface DocumentMeta {
  file_name: string;
  size_bytes: number;
  upload_date: string;
  folder: string;
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<string[]>([]);
  const [metadatas, setMetadatas] = useState<Record<string, DocumentMeta>>({});
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFolder, setSelectedFolder] = useState("All");
  const [folders, setFolders] = useState<string[]>(["All", "Default"]);
  
  // Modals / Inputs
  const [newFolderName, setNewFolderName] = useState("");
  const [showNewFolderInput, setShowNewFolderInput] = useState(false);
  const [renamingFile, setRenamingFile] = useState<string | null>(null);
  const [newFileName, setNewFileName] = useState("");

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const res = await api.get("/documents");
      const docList = res.data.documents || [];
      setDocuments(docList);
      
      const metaMap: Record<string, DocumentMeta> = {};
      const uniqueFolders = new Set<string>(["All", "Default"]);
      
      await Promise.all(
        docList.map(async (doc: string) => {
          try {
            const metaRes = await api.get(`/documents/${encodeURIComponent(doc)}/metadata`);
            metaMap[doc] = metaRes.data;
            if (metaRes.data.folder) {
              uniqueFolders.add(metaRes.data.folder);
            }
          } catch (err) {
            console.error("Failed to load metadata for", doc, err);
          }
        })
      );
      
      setMetadatas(metaMap);
      setFolders(Array.from(uniqueFolders));
    } catch (err) {
      console.error("Failed to fetch documents", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    
    setUploading(true);
    try {
      const formData = new FormData();
      Array.from(files).forEach((f) => formData.append("files", f));
      formData.append("folder", selectedFolder === "All" ? "Default" : selectedFolder);
      
      await api.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      
      setTimeout(async () => {
        await fetchDocuments();
        setUploading(false);
      }, 3000);
    } catch (err) {
      console.error("Upload failed", err);
      setUploading(false);
    }
  };

  const handleCreateFolder = () => {
    if (!newFolderName.trim()) return;
    const cleanName = newFolderName.trim();
    if (!folders.includes(cleanName)) {
      setFolders([...folders, cleanName]);
      setSelectedFolder(cleanName);
    }
    setNewFolderName("");
    setShowNewFolderInput(false);
  };

  const handleRename = async () => {
    if (!renamingFile || !newFileName.trim()) return;
    try {
      await api.post("/documents/rename", {
        old_name: renamingFile,
        new_name: newFileName.trim(),
      });
      setRenamingFile(null);
      setNewFileName("");
      await fetchDocuments();
    } catch (err) {
      console.error("Rename failed", err);
    }
  };

  const handleMoveFolder = async (fileName: string, targetFolder: string) => {
    try {
      await api.patch(`/documents/${encodeURIComponent(fileName)}/folder`, {
        folder: targetFolder,
      });
      await fetchDocuments();
    } catch (err) {
      console.error("Move folder failed", err);
    }
  };

  const filteredDocuments = documents.filter((doc) => {
    const meta = metadatas[doc];
    const matchesSearch = doc.toLowerCase().includes(searchQuery.toLowerCase());
    const docFolder = meta?.folder || "Default";
    const matchesFolder = selectedFolder === "All" || docFolder === selectedFolder;
    return matchesSearch && matchesFolder;
  });

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 flex flex-col transition-colors">
      {/* Header */}
      <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-6 py-4 flex items-center justify-between shadow-sm transition-colors">
        <div className="flex items-center gap-3">
          <Link href="/" className="p-2 hover:bg-gray-150 dark:hover:bg-gray-800 rounded-lg text-gray-500 dark:text-gray-400 transition">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <h1 className="text-lg font-bold text-gray-900 dark:text-gray-50">Document Manager Vault</h1>
        </div>
      </header>

      {/* Main Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* Folder Sidebar */}
        <aside className="w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 p-4 flex flex-col gap-4 flex-shrink-0 transition-colors">
          <div className="flex items-center justify-between px-2">
            <span className="text-xs font-bold text-gray-400 dark:text-gray-505 uppercase tracking-wider">Folders</span>
            <button
              onClick={() => setShowNewFolderInput(!showNewFolderInput)}
              className="p-1 hover:bg-gray-105 dark:hover:bg-gray-800 text-gray-500 hover:text-blue-500 rounded transition"
              title="Create Folder"
            >
              <FolderPlus className="w-4 h-4" />
            </button>
          </div>

          {showNewFolderInput && (
            <div className="p-2 border border-gray-150 dark:border-gray-800 rounded-xl space-y-2 bg-gray-50 dark:bg-gray-900/60">
              <input
                type="text"
                placeholder="Folder Name..."
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
                className="w-full text-xs bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-2 focus:ring-1 focus:ring-blue-500 outline-none"
              />
              <div className="flex gap-1.5 justify-end">
                <button onClick={handleCreateFolder} className="px-2.5 py-1 text-[10px] font-bold bg-blue-600 text-white rounded-lg hover:bg-blue-700">Add</button>
                <button onClick={() => setShowNewFolderInput(false)} className="px-2.5 py-1 text-[10px] font-bold bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300">Cancel</button>
              </div>
            </div>
          )}

          <div className="flex-1 overflow-y-auto space-y-1">
            {folders.map((folder) => (
              <button
                key={folder}
                onClick={() => setSelectedFolder(folder)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-left text-xs font-semibold transition ${
                  selectedFolder === folder
                    ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-bold"
                    : "text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
                }`}
              >
                <span className="flex items-center gap-2 truncate">
                  {selectedFolder === folder ? <FolderOpen className="w-4 h-4" /> : <Folder className="w-4 h-4" />}
                  <span className="truncate">{folder}</span>
                </span>
                <span className="text-[10px] bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded-full text-gray-500 font-medium">
                  {folder === "All"
                    ? documents.length
                    : documents.filter((d) => (metadatas[d]?.folder || "Default") === folder).length}
                </span>
              </button>
            ))}
          </div>
        </aside>

        {/* Content Panel */}
        <main className="flex-1 flex flex-col overflow-hidden bg-slate-50 dark:bg-slate-900 transition-colors p-6 gap-6">
          {/* Action Bar */}
          <div className="flex flex-col sm:flex-row gap-4 justify-between items-stretch sm:items-center bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800/80 rounded-2xl p-4 shadow-sm transition-colors">
            {/* Search Input */}
            <div className="flex-1 max-w-md relative">
              <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-3.5" />
              <input
                type="text"
                placeholder="Search documents by name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-1 focus:ring-blue-500 outline-none transition"
              />
            </div>

            {/* Upload Area */}
            <div className="flex items-center gap-3">
              <label className={`cursor-pointer bg-blue-600 hover:bg-blue-700 text-white rounded-xl py-2.5 px-4 flex items-center gap-2 font-medium text-xs shadow-md transition active:scale-95 ${uploading ? "opacity-60 pointer-events-none" : ""}`}>
                {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                {uploading ? "Indexing files..." : `Upload to ${selectedFolder === "All" ? "Default" : selectedFolder}`}
                <input type="file" multiple className="hidden" onChange={handleUpload} disabled={uploading} />
              </label>
            </div>
          </div>

          {/* Documents Grid */}
          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="flex justify-center py-20">
                <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
              </div>
            ) : filteredDocuments.length === 0 ? (
              <div className="text-center py-20 border-2 border-dashed border-gray-200 dark:border-gray-800 rounded-2xl bg-white dark:bg-gray-900 transition">
                <FileText className="w-10 h-10 text-gray-300 dark:text-gray-700 mx-auto mb-2" />
                <p className="text-xs text-gray-500 dark:text-gray-400 font-semibold">No documents found matching the filter</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredDocuments.map((doc) => {
                  const meta = metadatas[doc];
                  return (
                    <div key={doc} className="relative group bg-white dark:bg-gray-900 border border-gray-150 dark:border-gray-800/80 rounded-2xl p-4 shadow-sm hover:shadow-md transition">
                      <DocumentCard fileName={doc} onDelete={fetchDocuments} />
                      
                      <div className="mt-3 pt-3 border-t border-slate-50 dark:border-gray-800 flex justify-between items-center text-xs">
                        <span className="text-[10px] bg-slate-50 dark:bg-slate-800 px-2 py-0.5 rounded-full text-slate-500 dark:text-slate-400 font-semibold">
                          Folder: {meta?.folder || "Default"}
                        </span>
                        
                        <div className="flex gap-2">
                          <select
                            value={meta?.folder || "Default"}
                            onChange={(e) => handleMoveFolder(doc, e.target.value)}
                            className="bg-slate-50 dark:bg-slate-800 text-[10px] text-gray-500 dark:text-gray-400 border border-slate-100 dark:border-gray-700 rounded p-0.5 cursor-pointer outline-none"
                          >
                            {folders.filter(f => f !== "All").map(f => (
                              <option key={f} value={f}>{f}</option>
                            ))}
                          </select>
                          
                          <button
                            onClick={() => {
                              setRenamingFile(doc);
                              setNewFileName(doc);
                            }}
                            className="text-gray-400 hover:text-blue-500 transition"
                            title="Rename file"
                          >
                            <Edit2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </main>
      </div>

      {/* Rename Modal */}
      {renamingFile && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in" onClick={() => setRenamingFile(null)}>
          <div className="bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-2xl shadow-xl max-w-md w-full mx-4 p-6" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-base font-bold text-gray-900 dark:text-gray-50 mb-4">Rename Document</h3>
            <input
              type="text"
              value={newFileName}
              onChange={(e) => setNewFileName(e.target.value)}
              className="w-full text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-3 focus:ring-1 focus:ring-blue-500 outline-none mb-4"
            />
            <div className="flex gap-2 justify-end">
              <button onClick={handleRename} className="px-4 py-2 text-xs font-bold bg-blue-600 text-white rounded-xl hover:bg-blue-700">Rename</button>
              <button onClick={() => setRenamingFile(null)} className="px-4 py-2 text-xs font-bold bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-300">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
