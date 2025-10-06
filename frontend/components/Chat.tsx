'use client';
import { useState } from "react";

type Msg = { role: "user"|"assistant"; content: string };

export default function Chat() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState("coder");
  const [loading, setLoading] = useState(false);

  async function send() {
    if (!input.trim()) return;
    const next = [...messages, { role: "user", content: input } as Msg];
    setMessages(next); setInput(""); setLoading(true);
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: next, mode })
    });
    const data = await res.json();
    setMessages([...next, { role: "assistant", content: data.content }]);
    setLoading(false);
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2 items-center">
        <label className="text-sm">Mode</label>
        <select value={mode} onChange={(e)=>setMode(e.target.value)}
          className="border rounded px-2 py-1">
          <option value="architect">architect</option>
          <option value="coder">coder</option>
          <option value="debugger">debugger</option>
        </select>
      </div>
      <div className="border rounded p-3 min-h-[240px] space-y-3 bg-white">
        {messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'text-gray-900' : 'text-blue-900'}>
            <b>{m.role}:</b> <span>{m.content}</span>
          </div>
        ))}
        {loading && <div className="opacity-70">Thinking…</div>}
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 border rounded px-3 py-2"
          value={input}
          onChange={(e)=>setInput(e.target.value)}
          placeholder="Ask something…"
        />
        <button onClick={send} className="border rounded px-4">Send</button>
      </div>
    </div>
  );
}