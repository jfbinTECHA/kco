'use client';
import { useState } from 'react';

type Msg = { role: 'user' | 'assistant' | 'system'; content: string };

export default function PlannerPanel({ onConfirm }: { onConfirm: (plan: string[]) => void }) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState('');
  const [plan, setPlan] = useState<string[]>([]);
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);

  async function askPlanner() {
    const next = [...messages, { role: 'user', content: input }];
    setMessages(next); setLoading(true); setInput('');
    const res = await fetch('/api/plan', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ messages: next })});
    const json = await res.json();
    setPlan(Array.isArray(json.plan) ? json.plan : []);
    setSummary(json.summary || '');
    setLoading(false);
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-auto space-y-2 bg-white p-3 rounded border">
        {messages.map((m,i)=> (
          <div key={i}><b>{m.role}:</b> {m.content}</div>
        ))}
        {loading && <div className="opacity-70">Thinking…</div>}
        {plan.length>0 && (
          <div className="mt-3">
            <h3 className="font-semibold">Proposed Plan</h3>
            <ol className="list-decimal ml-5 space-y-1">
              {plan.map((s,i)=>(<li key={i}>{s}</li>))}
            </ol>
            {summary && <p className="mt-2 text-sm text-gray-600">{summary}</p>}
            <button onClick={()=>onConfirm(plan)} className="mt-3 border rounded px-3 py-1">Yes, run this with Kilo</button>
          </div>
        )}
      </div>
      <div className="mt-3 flex gap-2">
        <input className="flex-1 border rounded px-3 py-2" value={input} onChange={(e)=>setInput(e.target.value)} placeholder="Describe what to build…" />
        <button onClick={askPlanner} className="border rounded px-4">Plan</button>
      </div>
    </div>
  );
}