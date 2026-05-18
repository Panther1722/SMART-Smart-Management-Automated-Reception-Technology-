import React, { useEffect, useMemo, useRef, useState } from "react";

const PLACEHOLDER_GREETING =
  "Hi! I'm the (prototype) receptionist. What can I help you with today?";

function createSessionId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `sess-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}

export default function App() {
  const sessionIdRef = useRef(null);
  const [messages, setMessages] = useState(() => [
    {
      id: crypto.randomUUID(),
      role: "assistant",
      text: PLACEHOLDER_GREETING,
    },
  ]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);

  const listRef = useRef(null);
  const canSend = useMemo(() => !sending && draft.trim().length > 0, [sending, draft]);

  useEffect(() => {
    const el = listRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages, sending]);

  function getOrCreateSessionId() {
    if (!sessionIdRef.current) {
      sessionIdRef.current = createSessionId();
    }
    return sessionIdRef.current;
  }

  async function postChat(message, sessionId) {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`HTTP ${res.status}: ${errText || "Request failed"}`);
    }

    return res.json();
  }

  async function onSubmit(e) {
    e.preventDefault();
    const text = draft.trim();
    if (!text || sending) return;

    const sessionId = getOrCreateSessionId();
    setDraft("");
    setSending(true);

    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", text },
    ]);

    try {
      const data = await postChat(text, sessionId);
      if (data?.session_id) {
        sessionIdRef.current = data.session_id;
      }

      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          text: data?.reply ?? "Thanks — I've received your message.",
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          kind: "err",
          text: `Sorry — I couldn't send that message. ${err.message}`,
        },
      ]);
    } finally {
      setSending(false);
    }
  }

  return (
    <main className="container">
      <header className="header">
        <h1>AI Receptionist Prototype</h1>
        <p className="subtitle">
          Chat with the receptionist. Messages are saved via <code>/api/chat</code>.
        </p>
      </header>

      <section className="card">
        <div className="chat" aria-label="Chat">
          <div
            ref={listRef}
            className="messages"
            aria-live="polite"
            aria-relevant="additions"
          >
            {messages.map((m) => (
              <div
                key={m.id}
                className={`message ${m.role}${m.kind === "err" ? " err" : ""}`}
              >
                <div className="bubble">{m.text}</div>
              </div>
            ))}
            {sending ? (
              <div className="message assistant">
                <div
                  className="bubble loading"
                  aria-busy="true"
                  aria-label="Assistant is typing"
                >
                  <span className="typing-dots">
                    <span />
                    <span />
                    <span />
                  </span>
                </div>
              </div>
            ) : null}
          </div>

          <form className="composer" onSubmit={onSubmit} autoComplete="off">
            <label className="sr-only" htmlFor="messageInput">
              Message
            </label>
            <input
              id="messageInput"
              className="input"
              type="text"
              placeholder={sending ? "Waiting for reply…" : "Type a message…"}
              maxLength={2000}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              disabled={sending}
              required
            />
            <button className="primary" type="submit" disabled={!canSend}>
              {sending ? "Sending…" : "Send"}
            </button>
          </form>
        </div>
      </section>

      <footer className="footer">
        <a href="/docs" target="_blank" rel="noreferrer">
          Backend API Docs
        </a>
        <span className="dot">•</span>
        <a href="/api/booking-requests" target="_blank" rel="noreferrer">
          View Saved Requests (JSON)
        </a>
      </footer>
    </main>
  );
}
