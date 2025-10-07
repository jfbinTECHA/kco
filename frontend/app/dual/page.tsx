import DualPanel from "@/components/DualPanel";
export default function DualPage(){
  return (
    <main className="mx-auto max-w-6xl p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Planner ↔ Kilo (Dual Panel)</h1>
      <DualPanel />
    </main>
  );
}