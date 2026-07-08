// Thin fetch wrapper: base URL, JWT header, JSON handling, and SSE streaming.
import { useAuthStore } from "../store/authStore";

// Resolve the API base URL robustly. Accepts a full URL, a bare host (as Render
// injects via `fromService.host`), or nothing (local dev default).
function resolveBaseUrl() {
  let raw = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
  if (!/^https?:\/\//.test(raw)) raw = `https://${raw}`;
  raw = raw.replace(/\/+$/, "");
  if (!/\/api\/v\d+$/.test(raw)) raw = `${raw}/api/v1`;
  return raw;
}

const BASE_URL = resolveBaseUrl();

function authHeaders(extra = {}) {
  const token = useAuthStore.getState().accessToken;
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
  };
}

async function handle(res) {
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data?.detail;
    const message =
      typeof detail === "string" ? detail : detail?.reason || "Request failed";
    const err = new Error(message);
    err.status = res.status;
    err.detail = detail;
    throw err;
  }
  return data;
}

export const api = {
  base: BASE_URL,

  get: (path) => fetch(`${BASE_URL}${path}`, { headers: authHeaders() }).then(handle),

  post: (path, body) =>
    fetch(`${BASE_URL}${path}`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(body ?? {}),
    }).then(handle),

  patch: (path, body) =>
    fetch(`${BASE_URL}${path}`, {
      method: "PATCH",
      headers: authHeaders(),
      body: JSON.stringify(body ?? {}),
    }).then(handle),

  put: (path, body) =>
    fetch(`${BASE_URL}${path}`, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify(body ?? {}),
    }).then(handle),

  del: (path) =>
    fetch(`${BASE_URL}${path}`, { method: "DELETE", headers: authHeaders() }).then(
      handle
    ),

  upload: (path, formData) =>
    fetch(`${BASE_URL}${path}`, {
      method: "POST",
      headers: (() => {
        const token = useAuthStore.getState().accessToken;
        return token ? { Authorization: `Bearer ${token}` } : {};
      })(),
      body: formData,
    }).then(handle),
};

/**
 * Stream a chat answer over SSE.
 * Calls onMeta({conversation_id, sources}), onToken(text), onDone(), onError(err).
 */
export async function streamChat(payload, { onMeta, onToken, onDone, onError }) {
  const token = useAuthStore.getState().accessToken;
  try {
    const res = await fetch(`${BASE_URL}/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok || !res.body) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data?.detail?.reason || data?.detail || "Chat failed");
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const events = buffer.split("\n\n");
      buffer = events.pop() || "";
      for (const chunk of events) {
        const lines = chunk.split("\n");
        const event = lines.find((l) => l.startsWith("event:"))?.slice(6).trim();
        const dataLine = lines.find((l) => l.startsWith("data:"))?.slice(5).trim();
        if (!dataLine) continue;
        const data = JSON.parse(dataLine);
        if (event === "meta") onMeta?.(data);
        else if (event === "token") onToken?.(data.text);
        else if (event === "error") onError?.(new Error(data.detail));
        else if (event === "done") onDone?.(data);
      }
    }
    onDone?.();
  } catch (err) {
    onError?.(err);
  }
}
