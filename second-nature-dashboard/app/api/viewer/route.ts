import { NextResponse } from "next/server";
import { getChatGPTUser } from "../../chatgpt-auth";
import { isOwnerEmail } from "../../lib/analytics";

export const dynamic = "force-dynamic";

export async function GET() {
  const user = await getChatGPTUser();
  return NextResponse.json({ isOwner: isOwnerEmail(user?.email) }, { headers: { "Cache-Control": "no-store" } });
}
