import { notFound } from "next/navigation";
import { requireChatGPTUser } from "../chatgpt-auth";
import { isOwnerEmail } from "../lib/analytics";
import ActivityDashboard from "./ActivityDashboard";

export const dynamic = "force-dynamic";

export default async function ActivityPage() {
  const user = await requireChatGPTUser("/activity");
  if (!isOwnerEmail(user.email)) notFound();
  return <ActivityDashboard ownerEmail={user.email} />;
}
