'use client';

import { useState, useEffect } from 'react';

interface FileInfo {
  path: string;
  size: number;
  type: string;
}

interface IndexResult {
  files: FileInfo[];
  total_files: number;
  total_dirs: number;
}

export default function FileIndexView() {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [path, setPath] = useState('.');
  const [expanded, setExpanded] = useState(false);

  const indexFiles = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/tools/fs/index', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path, max_depth: 2 })
      });
      const result: IndexResult = await response.json();
      setFiles(result.files || []);
    } catch (error) {
      console.error('Failed to index files:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (expanded) {
      indexFiles();
    }
  }, [path, expanded]);

  if (!expanded) {
    return (
      <button
        onClick={() => setExpanded(true)}
        className="text-xs text-gray-600 hover:text-gray-800 border rounded px-2 py-1"
      >
        📁 Show Files
      </button>
    );
  }

  return (
    <div className="border rounded p-3 bg-gray-50 max-w-md">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-semibold">Project Files</h4>
        <button
          onClick={() => setExpanded(false)}
          className="text-xs text-gray-500 hover:text-gray-700"
        >
          ✕
        </button>
      </div>

      <div className="flex gap-2 mb-2">
        <input
          value={path}
          onChange={(e) => setPath(e.target.value)}
          className="flex-1 text-xs border rounded px-2 py-1"
          placeholder="Project path"
        />
        <button
          onClick={indexFiles}
          disabled={loading}
          className="text-xs border rounded px-2 py-1 disabled:opacity-50"
        >
          {loading ? '...' : '🔄'}
        </button>
      </div>

      <div className="max-h-32 overflow-y-auto text-xs space-y-1">
        {files.slice(0, 10).map((file, i) => (
          <div key={i} className="flex justify-between text-gray-700">
            <span className="truncate flex-1">{file.path}</span>
            <span className="text-gray-500 ml-2">
              {file.type === 'file' ? '📄' : '📁'} {file.size}b
            </span>
          </div>
        ))}
        {files.length > 10 && (
          <div className="text-gray-500 text-center">
            ... and {files.length - 10} more files
          </div>
        )}
      </div>
    </div>
  );
}