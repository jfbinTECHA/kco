'use client';

import { useState } from 'react';
import Chat from '../components/Chat';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold">KiloCode Standalone</h1>
      </div>

      <Chat />

      <div className="mb-32 grid text-center lg:mb-0 lg:grid-cols-4 lg:text-left">
        <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100">
          <h2 className="mb-3 text-2xl font-semibold">Architect</h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Plan and design your projects.
          </p>
        </div>

        <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100">
          <h2 className="mb-3 text-2xl font-semibold">Code</h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Write and modify code efficiently.
          </p>
        </div>

        <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100">
          <h2 className="mb-3 text-2xl font-semibold">Debug</h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Troubleshoot and fix issues.
          </p>
        </div>

        <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100">
          <h2 className="mb-3 text-2xl font-semibold">Ask</h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Get answers to any questions.
          </p>
        </div>
      </div>
    </main>
  );
}