import { useState, useEffect, useCallback } from "react";
import api from "@/lib/api";

export interface Session {
  id: string;
  title: string;
  created_at: string;
}

export function useSessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSessions = useCallback(async () => {
    try {
      const res = await api.get("/sessions");
      setSessions(res.data);
    } catch (err) {
      console.error("Failed to fetch sessions", err);
    } finally {
      setLoading(false);
    }
  }, []);

  const createSession = async (title: string) => {
    const res = await api.post("/sessions", { title });
    await fetchSessions();
    return res.data.id;
  };

  const deleteSession = async (id: string) => {
    await api.delete(`/sessions/${id}`);
    await fetchSessions();
  };

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return { sessions, loading, createSession, deleteSession, refreshSessions: fetchSessions };
}