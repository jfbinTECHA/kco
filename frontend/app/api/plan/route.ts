import { NextRequest, NextResponse } from "next/server";
export async function POST(req: NextRequest) {
  const body = await req.json();
  const backend = process.env.BACKEND_URL || "http://localhost:8001";
  const r = await fetch(`${backend}/plan`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(body) });
  const data = await r.text();
  return new NextResponse(data, { headers: {"Content-Type":"application/json"} });
}