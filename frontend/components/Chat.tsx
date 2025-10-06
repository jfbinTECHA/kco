'use client';
import { useState } from "react";

type Msg = { role: "user"|"assistant"; content: string };

export default function Chat() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState("coder");
  const [loading, setLoading] = useState(false);
  const [globalRules, setGlobalRules] = useState("Always be helpful, accurate, and concise.\nUse clear, professional language.\nProvide practical solutions.");
  const [projectRules, setProjectRules] = useState("Follow existing code style and conventions.\nMaintain backward compatibility.\nWrite comprehensive tests.");
  const [projectPath, setProjectPath] = useState(".");
  const [showRules, setShowRules] = useState(false);

  async function send() {
    if (!input.trim()) return;
    const next = [...messages, { role: "user", content: input } as Msg];
    setMessages(next); setInput(""); setLoading(true);

    // Add empty assistant message for streaming
    const assistantMessage = { role: "assistant" as const, content: "" };
    setMessages([...next, assistantMessage]);

    const eventSource = new EventSource("/api/chat/stream");

    eventSource.onmessage = (event) => {
      const data = event.data;
      if (data === "[DONE]") {
        eventSource.close();
        setLoading(false);
        return;
      }

      // Append token to assistant message
      setMessages(prev => {
        const newMessages = [...prev];
        const lastMsg = newMessages[newMessages.length - 1];
        if (lastMsg.role === "assistant") {
          lastMsg.content += data;
        }
        return newMessages;
      });
    };

    eventSource.onerror = () => {
      eventSource.close();
      setLoading(false);
    };

    // Start the stream
    fetch("/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: next,
        mode,
        custom_rules: { global: globalRules, project: projectRules },
        project_context: { path: projectPath }
      })
    }).catch(() => {
      eventSource.close();
      setLoading(false);
    });
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
          <option value="ask">ask</option>
        </select>
        <button onClick={() => setShowRules(!showRules)}
          className="border rounded px-3 py-1 text-sm">
          {showRules ? 'Hide' : 'Show'} Rules
        </button>
      </div>

      {showRules && (
        <div className="border rounded p-3 bg-gray-50">
          <h3 className="text-sm font-semibold mb-2">Custom Rules</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium">Global Rules</label>
              <textarea
                value={globalRules}
                onChange={(e) => setGlobalRules(e.target.value)}
                className="w-full h-24 border rounded p-2 text-xs mt-1"
                placeholder="Global rules apply to all interactions..."
              />
            </div>
            <div>
              <label className="text-xs font-medium">Project Rules</label>
              <textarea
                value={projectRules}
                onChange={(e) => setProjectRules(e.target.value)}
                className="w-full h-24 border rounded p-2 text-xs mt-1"
                placeholder="Project rules apply to this specific project..."
              />
            </div>
          </div>
        </div>
      )}

      <div className="flex gap-2 items-center">
        <label className="text-sm">Project Path</label>
        <input
          value={projectPath}
          onChange={(e) => setProjectPath(e.target.value)}
          className="flex-1 border rounded px-2 py-1 text-sm"
          placeholder="Path to project directory (e.g., . or /path/to/project)"
        />
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