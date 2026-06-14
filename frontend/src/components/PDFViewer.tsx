"use client";

interface PDFViewerProps {
  filePath: string;       // e.g. "uploads/filename.pdf"
  pageNumber: number;     // page to jump to
  onClose: () => void;
}

export default function PDFViewer({ filePath, pageNumber, onClose }: PDFViewerProps) {
  // Build the full URL to the PDF file (backend serves static files at /static/uploads/filename.pdf)
  const pdfUrl = `http://localhost:8000/static/${encodeURIComponent(filePath)}#page=${pageNumber}`;

  return (
    <div 
      className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fade-in" 
      onClick={onClose}
    >
      <div 
        className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl w-full max-w-5xl h-[85vh] flex flex-col overflow-hidden border border-gray-200 dark:border-gray-800 animate-scale-up" 
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center px-6 py-4 border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50">
          <div className="flex items-center gap-3">
            <span className="p-2 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </span>
            <div>
              <h3 className="text-sm font-semibold text-gray-800 dark:text-gray-200 truncate max-w-lg">
                {filePath.split('/').pop()}
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Viewing page {pageNumber}
              </p>
            </div>
          </div>
          <button 
            onClick={onClose} 
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800/80"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="flex-1 bg-gray-100 dark:bg-gray-950 p-4">
          <iframe 
            src={pdfUrl} 
            className="w-full h-full border-0 rounded-lg shadow-sm bg-white dark:bg-gray-900" 
            title="PDF Preview"
          />
        </div>
      </div>
    </div>
  );
}
