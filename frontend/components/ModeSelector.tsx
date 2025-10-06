interface ModeSelectorProps {
  mode: string;
  onModeChange: (mode: string) => void;
}

export default function ModeSelector({ mode, onModeChange }: ModeSelectorProps) {
  return (
    <select value={mode} onChange={e => onModeChange(e.target.value)}
      className="border rounded px-2 py-1">
      <option value="architect">Architect</option>
      <option value="coder">Coder</option>
      <option value="debugger">Debugger</option>
      <option value="ask">Ask</option>
    </select>
  );
}