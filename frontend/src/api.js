// Thin API client. Vite proxies /api and /health to the FastAPI backend.

async function handle(res) {
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      if (body.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  chat: (sessionId, message) =>
    fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message }),
    }).then(handle),

  upload: (sessionId, file) => {
    const fd = new FormData();
    fd.append("session_id", sessionId);
    fd.append("file", file);
    return fetch("/api/upload", { method: "POST", body: fd }).then(handle);
  },

  saveComplaint: (sessionId, form, risk, summary) =>
    fetch("/api/complaints", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, form, risk, summary }),
    }).then(handle),

  listComplaints: () => fetch("/api/complaints").then(handle),
};
