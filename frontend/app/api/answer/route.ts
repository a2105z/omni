/**
 * POST /api/answer - Proxies to backend Phase 3 /api/answer when BACKEND_URL is set.
 * Uses the Omni backend's full synthesis pipeline: search -> context assembly -> citation-aware streaming.
 * If BACKEND_URL is not set, returns 503 with instructions.
 */
import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL;

export async function POST(req: Request) {
  if (!BACKEND_URL) {
    return NextResponse.json(
      {
        error: "Backend not configured",
        message:
          "Set BACKEND_URL or NEXT_PUBLIC_BACKEND_URL to use the Phase 3 synthesis pipeline.",
      },
      { status: 503 }
    );
  }

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const url = `${BACKEND_URL.replace(/\/$/, "")}/api/answer`;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 120_000); // 2 min

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (!res.ok) {
      const err = await res.text();
      return NextResponse.json(
        { error: `Backend error: ${res.status}`, details: err },
        { status: res.status }
      );
    }

    return new Response(res.body, {
      headers: {
        "Content-Type": res.headers.get("Content-Type") || "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  } catch (e) {
    clearTimeout(timeout);
    return NextResponse.json(
      { error: "Backend unreachable", message: (e as Error).message },
      { status: 502 }
    );
  }
}
