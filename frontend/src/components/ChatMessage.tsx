"use client";

import type { Message } from "@/lib/types";

interface Props {
  message: Message;
}

export default function ChatMessage({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-2 ${
          isUser
            ? "bg-blue-600 text-white rounded-br-sm"
            : "bg-gray-100 text-gray-900 rounded-bl-sm"
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5 border-t border-gray-300 pt-2">
            {message.citations.map((c, i) => (
              <button
                key={i}
                type="button"
                onClick={() => console.log(c.snippet)}
                className="inline-flex items-center gap-1 rounded-full bg-gray-200 px-2.5 py-0.5 text-xs font-medium text-gray-700 hover:bg-gray-300"
              >
                {c.file} (p.&nbsp;{c.page})
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
