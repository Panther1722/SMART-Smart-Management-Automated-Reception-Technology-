const btn = document.getElementById("sendBtn");
const statusEl = document.getElementById("status");

function setStatus(kind, text) {
  statusEl.classList.remove("ok", "err");
  if (kind) statusEl.classList.add(kind);
  statusEl.textContent = text;
}

async function sendBookingRequest() {
  btn.disabled = true;
  setStatus(null, "Sending booking request…");

  try {
    const res = await fetch("/api/booking-request", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "Booking request submitted from prototype" }),
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`HTTP ${res.status}: ${errText || "Request failed"}`);
    }

    const data = await res.json();
    setStatus("ok", `Success. Saved request #${data.id} at ${data.created_at}.`);
  } catch (e) {
    setStatus("err", `Failed to send booking request: ${e.message}`);
  } finally {
    btn.disabled = false;
  }
}

btn.addEventListener("click", sendBookingRequest);
setStatus(null, "Ready. Click the button to submit one booking request.");

