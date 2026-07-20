import { NextResponse } from "next/server";
import { env } from "cloudflare:workers";

export const dynamic = "force-dynamic";

export async function GET() {
  const bindings = env as unknown as { ANTHROPIC_API_KEY?: string };
  const available = Boolean(bindings.ANTHROPIC_API_KEY || process.env.ANTHROPIC_API_KEY);
  return NextResponse.json({ available, live: available }, { headers: { "Cache-Control": "no-store" } });
}
