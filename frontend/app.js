const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const btn = document.getElementById("sendBtn");
const messagesEl = document.getElementById("messages");

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function formatTimestamp(isoLikeString) {
  if (!isoLikeString) return "";
  const dt = new Date(isoLikeString);
  if (Number.isNaN(dt.getTime())) return String(isoLikeString);
  return dt.toLocaleString();
}

function appendMessage(role, text, { kind = "normal", meta = "" } = {}) {
  const row = document.createElement("div");
  row.className = `message ${role}${kind === "err" ? " err" : ""}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  row.appendChild(bubble);

  if (meta) {
    const metaEl = document.createElement("div");
    metaEl.className = "meta";
    metaEl.textContent = meta;
    bubble.appendChild(metaEl);
  }

  messagesEl.appendChild(row);
  scrollToBottom();
}

async function postBookingRequest(message) {
  const res = await fetch("/api/booking-request", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`HTTP ${res.status}: ${errText || "Request failed"}`);
  }

  return await res.json();
}

async function onSend(text) {
  const trimmed = text.trim();
  if (!trimmed) return;

  input.value = "";
  input.focus();

  appendMessage("user", trimmed);

  btn.disabled = true;
  input.disabled = true;

  try {
    const data = await postBookingRequest(trimmed);
    const meta = data?.id ? `Saved as request #${data.id}${data?.created_at ? ` • ${formatTimestamp(data.created_at)}` : ""}` : "";
    appendMessage("assistant", "Thanks — I’ve saved your message. (LLM not connected yet.)", { meta });
  } catch (e) {
    appendMessage("assistant", `Sorry — I couldn’t save that message. ${e.message}`, {
      kind: "err",
      meta: "Check that Docker is running and the backend is reachable via /api.",
    });
  } finally {
    btn.disabled = false;
    input.disabled = false;
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  onSend(input.value);
});

appendMessage("assistant", "Hi! I’m the (prototype) receptionist. What can I help you with today?", {
  meta: "Tip: Send a message to store it via the API.",
});

