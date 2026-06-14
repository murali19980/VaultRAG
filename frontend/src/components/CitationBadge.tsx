import { useState } from "react";
import { FileText } from "lucide-react";

interface Citation {
  file: string;
  page: string;
  snippet?: string;
  text?: string;
}

interface CitationBadgeProps {
  citation: Citation;
  onViewPDF: (fileName: string, pageNum: number) => void;
}

export default function CitationBadge({ citation, onViewPDF }: CitationBadgeProps) {
  const [show, setShow] = useState(false);
  const displayText = citation.snippet || citation.text || "No snippet available";
  const pageNum = parseInt(citation.page, 10) || 1;

  return (
    <span className="relative inline-block">
      <span
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        onClick={() => onViewPDF(citation.file, pageNum)}
        className="inline-flex items-center gap-1 bg-blue-50 text-blue-700 hover:bg-blue-100 dark:bg-blue-900/40 dark:text-blue-300 dark:hover:bg-blue-900/60 border border-blue-200 dark:border-blue-800 text-xs font-medium rounded-full px-2.5 py-0.5 cursor-pointer transition-colors active:scale-95"
      >
        <FileText size={10} />
        {citation.file} (p.{citation.page})
      </span>
      {show && (
        <div className="absolute z-50 bottom-full left-0 mb-2 w-72 bg-gray-900 text-gray-100 text-xs rounded-lg shadow-xl p-3 border border-gray-800 whitespace-normal leading-relaxed">
          <p className="font-semibold text-blue-400 mb-1 border-b border-gray-800 pb-1">
            Citation Snippet:
          </p>
          {displayText}
        </div>
      )}
    </span>
  );
}