import { useState, useCallback } from "react";
import api from "@/lib/api";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: any[];
}

export function useChat(sessionId: string | null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = useCallback(async (content: string) => {
    if (!sessionId) return;
    setLoading(true);
    
    // Add user message immediately
    const userMsgId = crypto.randomUUID();
    setMessages(prev => [...prev, { id: userMsgId, role: "user", content }]);

    try {
      const res = await api.post("/chat", {
        session_id: sessionId,
        message: content
      });
      
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: res.data.answer,
        citations: res.data.citations || []
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      console.error("Failed to send message", err);
      const errorMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "Sorry, something went wrong while processing your request. Please try again."
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const loadMessages = useCallback(async (sid: string | null) => {
    if (!sid) {
      setMessages([]);
      return;
    }
    setLoading(true);
    try {
      const res = await api.get(`/sessions/${sid}/messages`);
      setMessages(
        res.data.map((m: any) => ({
          id: m.id,
          role: m.role as "user" | "assistant",
          content: m.content,
          citations: m.citations ? JSON.parse(m.citations) : []
        }))
      );
    } catch (err) {
      console.error("Failed to load messages", err);
      setMessages([]);
    } finally {
      setLoading(false);
    }
  }, []);

  return { messages, loading, sendMessage, loadMessages };
}
