"use client";

import { useCallback, useState } from "react";

export interface BackendAnswerMeta {
  sources: { url: string; title: string; snippet?: string; domain?: string }[];
  image_sources?: {
    sourceNumber: number;
    imgUrl: string;
    title: string;
    summary?: string;
  }[];
}

export interface UseBackendAnswerResult {
  streamAnswer: (
    query: string,
    opts: {
      mode?: string;
      onMeta?: (meta: BackendAnswerMeta) => void;
      onChunk?: (text: string) => void;
      onDone?: (followUps: string[]) => void;
      onError?: (err: string) => void;
      signal?: AbortSignal;
    }
  ) => Promise<void>;
  isStreaming: boolean;
}

export function useBackendAnswer(): UseBackendAnswerResult {
  const [isStreaming, setIsStreaming] = useState(false);

  const streamAnswer = useCallback(
    async (
      query: string,
      opts: {
        mode?: string;
        onMeta?: (meta: BackendAnswerMeta) => void;
        onChunk?: (text: string) => void;
        onDone?: (followUps: string[]) => void;
        onError?: (err: string) => void;
        signal?: AbortSignal;
      }
    ) => {
      setIsStreaming(true);
      try {
        const res = await fetch("/api/answer", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query,
            mode: opts.mode || "general",
            limit: 10,
            include_images: true,
          }),
          signal: opts.signal,
        });

        if (!res.ok) {
          const j = await res.json().catch(() => ({}));
          opts.onError?.(j.error || j.message || `HTTP ${res.status}`);
          return;
        }

        const reader = res.body?.getReader();
        if (!reader) {
          opts.onError?.("No response body");
          return;
        }

        const dec = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += dec.decode(value, { stream: true });
          const blocks = buffer.split("\n\n");
          buffer = blocks.pop() ?? "";
          for (const block of blocks) {
            const eventMatch = block.match(/^event:\s*(.+)/m);
            const dataMatch = block.match(/^data:\s*(.+)/m);
            if (!eventMatch || !dataMatch) continue;
            const event = eventMatch[1].trim();
            try {
              const data = JSON.parse(dataMatch[1].trim());
              if (event === "meta") opts.onMeta?.(data);
              else if (event === "chunk") opts.onChunk?.(data.text ?? "");
              else if (event === "done") opts.onDone?.(data.follow_ups ?? []);
              else if (event === "error")
                opts.onError?.(data.error ?? "Unknown error");
            } catch {
              /* skip */
            }
          }
        }
      } catch (e) {
        if ((e as Error).name !== "AbortError") {
          opts.onError?.((e as Error).message ?? "Request failed");
        }
      } finally {
        setIsStreaming(false);
      }
    },
    []
  );

  return { streamAnswer, isStreaming };
}
