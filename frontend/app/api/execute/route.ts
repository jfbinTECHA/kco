import { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  const backend = process.env.BACKEND_URL || "http://localhost:8001";
  const body = await req.text();
  const r = await fetch(`${backend}/execute`, { method: 'POST', body, headers: { 'Content-Type': 'application/json' } });

  // Proxy SSE stream
  const readable = new ReadableStream({
    async start(controller) {
      const reader = (r.body as ReadableStream<Uint8Array>).getReader();
      const dec = new TextDecoder();
      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;
        controller.enqueue(value);
      }
      controller.close();
    },
  });

  return new Response(readable, { headers: { "Content-Type": "text/event-stream" } });
}