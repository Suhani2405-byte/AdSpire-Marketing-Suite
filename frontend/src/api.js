import axios from "axios";

// Same-origin in production (Flask serves the build); Vite proxies /api in dev.
export const API_BASE = "/api";
const TOKEN_KEY = "adspire_token";

export const getToken = () => {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
};

export const setToken = (token) => {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* storage blocked (private mode) - session just won't persist */
  }
};

export const api = axios.create({ baseURL: API_BASE });

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let onUnauthorized = () => {};
export const setUnauthorizedHandler = (fn) => {
  onUnauthorized = fn;
};

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err?.response?.status === 401 && err.response.data?.auth === false) onUnauthorized();
    return Promise.reject(err);
  }
);

export const apiError = (err, fallback = "Something went wrong.") =>
  err?.response?.data?.error ||
  (err?.code === "ECONNABORTED" ? "Request timed out." : null) ||
  (err?.response ? fallback : "Cannot reach the backend server. Is it running on port 5000?");

/**
 * Stream campaign generation (Server-Sent Events over a POST).
 * onEvent receives {type: "status"|"chunk"|"reset"|"done"|"error", ...}.
 * Resolves with the final "done" event.
 */
export async function streamCampaign(payload, onEvent, signal) {
  const res = await fetch(`${API_BASE}/campaigns/generate-stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${getToken() || ""}` },
    body: JSON.stringify(payload),
    signal,
  });

  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      msg = body.error || msg;
      if (res.status === 401 && body.auth === false) onUnauthorized();
    } catch {
      /* non-JSON error body */
    }
    throw new Error(msg);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let final = null;

  for (;;) {
    let chunk;
    try {
      chunk = await reader.read();
    } catch (e) {
      if (e?.name === "AbortError" || signal?.aborted) throw e;
      // e.g. "Error in input stream" when the server restarts or the network drops mid-stream
      throw new Error("The connection to the server was lost while generating. Please try again.");
    }
    const { value, done } = chunk;
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let idx;
    while ((idx = buffer.indexOf("\n\n")) >= 0) {
      const raw = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      const line = raw.split("\n").find((l) => l.startsWith("data: "));
      if (!line) continue;
      const event = JSON.parse(line.slice(6));
      if (event.type === "error") throw new Error(event.error || "Generation failed.");
      if (event.type === "done") final = event;
      onEvent(event);
    }
  }
  if (!final) throw new Error("The connection closed before the campaign finished.");
  return final;
}
