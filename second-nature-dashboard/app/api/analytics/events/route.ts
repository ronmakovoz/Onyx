import { NextResponse } from "next/server";
import { parseAnalyticsEvent, recordAnalyticsEvent } from "../../../lib/analytics";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid analytics event." }, { status: 400 });
  }

  const event = parseAnalyticsEvent(body);
  if (!event) return NextResponse.json({ error: "Invalid analytics event." }, { status: 400 });

  await recordAnalyticsEvent(event, request);
  return new NextResponse(null, { status: 204, headers: { "Cache-Control": "no-store" } });
}
