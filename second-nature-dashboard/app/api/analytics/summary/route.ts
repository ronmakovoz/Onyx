import { NextResponse } from "next/server";
import { getChatGPTUser } from "../../../chatgpt-auth";
import { getAnalyticsSummary, isOwnerEmail, type AnalyticsRange } from "../../../lib/analytics";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const user = await getChatGPTUser();
  if (!isOwnerEmail(user?.email)) return NextResponse.json({ error: "Not found." }, { status: 404 });
  const requestedRange = new URL(request.url).searchParams.get("range");
  const range: AnalyticsRange = requestedRange === "24h" || requestedRange === "30d" ? requestedRange : "7d";
  const summary = await getAnalyticsSummary(range);
  return NextResponse.json(summary, { headers: { "Cache-Control": "no-store" } });
}
