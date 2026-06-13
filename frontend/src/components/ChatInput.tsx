import React, { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";

interface Props {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: Props) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (!input.trim() || disabled) return;
    onSend(input.trim());
    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  return (
    <div className="border-t border-gray-100 bg-white/80 backdrop-blur-md p-4 flex gap-2 items-end shadow-lg">
      <div className="flex-1 relative rounded-xl border border-gray-200 shadow-sm focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 bg-white transition-all">
        <textarea
          ref={textareaRef}
          rows={1}
          className="w-full pl-4 pr-12 py-3 resize-none bg-transparent focus:outline-none text-sm text-gray-800 placeholder-gray-400 max-h-36 overflow-y-auto"
          placeholder={disabled ? "Please wait..." : "Ask a question about your documents..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
        />
        <button
          onClick={handleSubmit}
          disabled={disabled || !input.trim()}
          className="absolute right-2 bottom-2 bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors shadow-sm"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}