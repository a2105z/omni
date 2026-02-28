import { NextResponse } from "next/server";

export async function GET() {
  const keys = {
    BRAVE_API_KEY: !!process.env.BRAVE_API_KEY,
    OPENAI_API_KEY: !!process.env.OPENAI_API_KEY,
    CEREBRAS_API_KEY: !!process.env.CEREBRAS_API_KEY,
    GROQ_API_KEY: !!process.env.GROQ_API_KEY,
    BACKEND_URL: !!process.env.BACKEND_URL || !!process.env.NEXT_PUBLIC_BACKEND_URL,
  };

  const missing = Object.entries(keys)
    .filter(([, v]) => !v)
    .map(([k]) => k);

  const critical = ["BRAVE_API_KEY", "OPENAI_API_KEY"].filter(
    (k) => !keys[k as keyof typeof keys]
  );

  return NextResponse.json({
    status: critical.length === 0 ? "ok" : "misconfigured",
    keys,
    missing,
    critical,
    message:
      critical.length > 0
        ? `Critical keys missing: ${critical.join(", ")}. Add them in Vercel → Settings → Environment Variables, then redeploy.`
        : "All critical keys configured.",
  });
}
