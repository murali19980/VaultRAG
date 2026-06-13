export interface Citation {
  page: string;
  file: string;
  snippet: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
}

export interface ChatRequest {
  session_id?: string;
  message: string;
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  citations: Citation[];
}
