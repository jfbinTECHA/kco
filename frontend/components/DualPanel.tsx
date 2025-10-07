'use client';
import { useState } from 'react';
import PlannerPanel from './PlannerPanel';
import KiloPanel from './KiloPanel';

export default function DualPanel(){
  const [plan, setPlan] = useState<string[]>([]);
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-[80vh]">
      <div className="h-full"><PlannerPanel onConfirm={setPlan} /></div>
      <div className="h-full"><KiloPanel plan={plan} /></div>
    </div>
  );
}