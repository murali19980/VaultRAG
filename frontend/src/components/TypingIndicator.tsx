export default function TypingIndicator() {
  return (
    <div className="flex space-x-1.5 items-center p-3 bg-white rounded-lg shadow-sm border border-gray-100 max-w-[80px]">
      <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
      <div className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
      <div className="w-2.5 h-2.5 bg-blue-300 rounded-full animate-bounce"></div>
    </div>
  );
}