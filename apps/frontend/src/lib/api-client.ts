const API_BASE = "/api/v1";

// Inject user's API key if available
function withApiKey(body: any): any {
  if (typeof window === "undefined") return body;
  const key = localStorage.getItem("stockwise_user_api_key");
  if (key) return { ...body, api_key: key };
  return body;
}

export async function apiGet<T = unknown>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `API error: ${res.status}`);
  }
  return res.json();
}

export async function apiPost<T = unknown>(
  path: string,
  body: unknown
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(withApiKey(body)),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `API error: ${res.status}`);
  }
  return res.json();
}

export function createSSERequest(
  path: string,
  body: unknown
): Promise<ReadableStream<Uint8Array>> {
  return fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(withApiKey(body)),
  }).then((res) => {
    if (!res.ok) throw new Error(`SSE error: ${res.status}`);
    return res.body!;
  });
}
