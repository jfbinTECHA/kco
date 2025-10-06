interface ModeSelectorProps {
  mode: string;
  onModeChange: (mode: string) => void;
}

const modeIcons = {
  architect: "🏗️",
  coder: "💻",
  debugger: "🔍",
  ask: "❓"
};

const modeLabels = {
  architect: "Architect",
  coder: "Coder",
  debugger: "Debugger",
  ask: "Ask"
};

export default function ModeSelector({ mode, onModeChange }: ModeSelectorProps) {
  return (
    <select value={mode} onChange={e => onModeChange(e.target.value)}
      className="border rounded px-3 py-2 bg-white">
      {Object.entries(modeLabels).map(([value, label]) => (
        <option key={value} value={value}>
          {modeIcons[value as keyof typeof modeIcons]} {label}
        </option>
      ))}
    </select>
  );
}