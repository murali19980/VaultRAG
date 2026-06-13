import React, { useRef } from "react";
import { Upload } from "lucide-react";
import { useUpload } from "@/hooks/useUpload";

interface Props {
  onUploadComplete?: (filenames: string[]) => void;
}

export default function FileUploader({ onUploadComplete }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const { uploadFiles, uploading, error } = useUpload();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    
    try {
      await uploadFiles(files);
      if (onUploadComplete) {
        onUploadComplete(Array.from(files).map(f => f.name));
      }
    } catch (err) {
      console.error("Upload failed", err);
    } finally {
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    }
  };

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,.xlsx,.csv"
        multiple
        className="hidden"
        onChange={handleFileChange}
      />
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        disabled={uploading}
        className="w-full inline-flex items-center justify-center gap-2 rounded-lg border border-dashed border-gray-700 hover:border-gray-500 px-4 py-2.5 text-sm font-medium text-gray-300 hover:text-white disabled:opacity-50 transition-all cursor-pointer"
      >
        <Upload size={16} />
        {uploading ? "Uploading…" : "Upload documents"}
      </button>
      {error && (
        <div className="text-red-400 text-xs mt-1 text-center truncate">
          {error}
        </div>
      )}
    </div>
  );
}
