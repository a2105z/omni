"use server";

/**
 * Stream answer from backend Phase 3 /api/answer when BACKEND_URL is set.
 * Returns async generator of { type, data } or null if backend unavailable.
 */
const BACKEND_URL =
  process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL;

export interface BackendAnswerMeta {
  sources: { url: string; title: string; snippet?: string; domain?: string }[];
  image_sources?: { sourceNumber: number; imgUrl: string; title: string; summary?: string }[];
  processed_query?: Record<string, unknown>;
}

export interface BackendAnswerChunk {
  text: string;
}

export interface BackendAnswerDone {
  follow_ups: string[];
}

export async function* streamBackendAnswer(
  query: string,
  options: {
    mode?: string;
    limit?: number;
    includeImages?: boolean;
    signal?: AbortSignal;
  } = {}
): AsyncGenerator<
  { type: "meta"; data: BackendAnswerMeta } | { type: "chunk"; data: BackendAnswerChunk } | { type: "done"; data: BackendAnswerDone } | { type: "error"; data: { error: string } },
  void,
  unknown
> {
  if (!BACKEND_URL) {
    yield { type: "error", data: { error: "Backend not configured" } };
    return;
  }

  const url = `${BACKEND_URL.replace(/\/$/, "")}/api/answer`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      mode: options.mode || "general",
      limit: options.limit ?? 10,
      include_images: options.includeImages ?? true,
    }),
    signal: options.signal,
  });

  if (!res.ok) {
    const err = await res.text();
    yield { type: "error", data: { error: err || `HTTP ${res.status}` } };
    return;
  }

  const reader = res.body?.getReader();
  if (!reader) {
    yield { type: "error", data: { error: "No response body" } };
    return;
  }

  const dec = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += dec.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() ?? "";
      for (const block of lines) {
        const eventMatch = block.match(/^event:\s*(.+)/m);
        const dataMatch = block.match(/^data:\s*(.+)/m);
        if (!eventMatch || !dataMatch) continue;
        const event = eventMatch[1].trim();
        try {
          const data = JSON.parse(dataMatch[1].trim());
          if (event === "meta") yield { type: "meta", data };
          else if (event === "chunk") yield { type: "chunk", data };
          else if (event === "done") yield { type: "done", data };
          else if (event === "error") yield { type: "error", data };
        } catch {
          // skip parse errors
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export function isBackendAvailable(): boolean {
  return !!BACKEND_URL;
}
