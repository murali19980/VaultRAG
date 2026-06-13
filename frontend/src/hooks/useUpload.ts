import { useState } from "react";
import api from "@/lib/api";

export function useUpload() {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const uploadFiles = async (files: FileList | File[]) => {
    setUploading(true);
    setError(null);
    setProgress(10);
    const formData = new FormData();
    Array.from(files).forEach(f => formData.append("files", f));
    
    try {
      // Simulate progress (since FastAPI doesn't report progress by default)
      const interval = setInterval(() => setProgress(p => Math.min(p + 10, 90)), 200);
      const res = await api.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      clearInterval(interval);
      setProgress(100);
      setTimeout(() => setProgress(0), 1000);
      return res.data;
    } catch (err: any) {
      setError(err.message || "Upload failed");
      setProgress(0);
      throw err;
    } finally {
      setUploading(false);
    }
  };

  return { uploading, progress, error, uploadFiles };
}