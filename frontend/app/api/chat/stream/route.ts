import { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const backend = process.env.BACKEND_URL || "http://localhost:8001";

  const response = await fetch(`${backend}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    return new Response("Streaming failed", { status: response.status });
  }

  // Return the streaming response as-is
  return new Response(response.body, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}