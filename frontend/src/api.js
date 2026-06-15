const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = data?.detail ?? data?.message ?? data;
    const message = typeof detail === "string" ? detail : JSON.stringify(detail);
    throw new Error(message && message !== "null" ? message : `Error HTTP ${response.status}`);
  }
  return data;
}

export const api = {
  chat: (payload) => request("/api/ai/chat", { method: "POST", body: JSON.stringify(payload) }),
  validateComplaint: (payload) =>
    request("/api/complaints/validate", { method: "POST", body: JSON.stringify(payload) }),
  createComplaint: (payload) => request("/api/complaints", { method: "POST", body: JSON.stringify(payload) }),
  getComplaint: (code) => request(`/api/complaints/${encodeURIComponent(code)}`),
  track: (code) => request(`/api/tracking/${encodeURIComponent(code)}`),
  adminList: (params = {}) => {
    const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value)).toString();
    return request(`/api/admin/complaints${query ? `?${query}` : ""}`);
  },
  updateStatus: (id, status) =>
    request(`/api/admin/complaints/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) }),
};
