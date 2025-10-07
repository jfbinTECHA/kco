'use client';
import { useEffect, useRef, useState } from 'react';

export default function KiloPanel({ plan }: { plan: string[] }) {
  const [lines, setLines] = useState<string[]>([]);
  const srcRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!plan || plan.length === 0) return;

    const start = async () => {
      // Start SSE by POSTing plan
      const controller = new AbortController();
      const body = JSON.stringify({ mode: 'coder', plan });

      // Create a local relay that opens SSE stream
      const res = await fetch('/api/execute', { method: 'POST', body, headers: { 'Content-Type': 'application/json' } });
      const reader = res.body?.getReader();
      const dec = new TextDecoder();
      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = dec.decode(value);
        const parts = chunk.split('\n\n').filter(Boolean);
        setLines(prev => [...prev, ...parts.map(p => p.replace(/^data: /, ''))]);
      }
    };

    start();
    return () => { try { srcRef.current?.close(); } catch {} };
  }, [JSON.stringify(plan)]);

  return (
    <div className="h-full bg-black text-green-300 font-mono p-3 rounded border overflow-auto">
      {lines.map((ln,i)=> (<div key={i}>{ln}</div>))}
    </div>
  );
}