import os
import mimetypes
from typing import List, Dict, Any, Optional
from pathlib import Path

class FileSystemTool:
    """Safe, read-only filesystem operations for AI assistance"""

    def __init__(self, allowed_paths: Optional[List[str]] = None):
        # Default to current working directory if no paths specified
        self.allowed_paths = allowed_paths or [os.getcwd()]
        self.max_file_size = 1024 * 1024  # 1MB limit
        self.max_snippet_length = 2000  # Max characters per snippet

    def _is_path_allowed(self, path: str) -> bool:
        """Check if a path is within allowed directories"""
        try:
            real_path = os.path.realpath(path)
            return any(os.path.commonpath([real_path, allowed]) == allowed
                      for allowed in self.allowed_paths)
        except (ValueError, OSError):
            return False

    def _is_text_file(self, file_path: str) -> bool:
        """Check if file is likely text-based"""
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and mime_type.startswith('text/'):
            return True

        # Check for common text file extensions
        text_extensions = {'.txt', '.md', '.py', '.js', '.ts', '.html', '.css',
                          '.json', '.xml', '.yaml', '.yml', '.ini', '.cfg',
                          '.sh', '.bash', '.sql', '.csv'}
        return Path(file_path).suffix.lower() in text_extensions

    def index_directory(self, path: str = ".", max_depth: int = 3) -> Dict[str, Any]:
        """Index directory structure and provide file information"""
        if not self._is_path_allowed(path):
            return {"error": f"Access denied: {path}"}

        try:
            result = {
                "path": path,
                "files": [],
                "directories": [],
                "total_files": 0,
                "total_dirs": 0
            }

            for root, dirs, files in os.walk(path):
                # Calculate depth
                depth = len(Path(root).relative_to(path).parts) if root != path else 0
                if depth > max_depth:
                    continue

                # Add directories
                for d in dirs:
                    if depth < max_depth:
                        result["directories"].append(os.path.join(root, d))
                        result["total_dirs"] += 1

                # Add files with metadata
                for f in files:
                    file_path = os.path.join(root, f)
                    if self._is_path_allowed(file_path):
                        file_info = {
                            "path": file_path,
                            "name": f,
                            "size": os.path.getsize(file_path),
                            "is_text": self._is_text_file(file_path)
                        }
                        result["files"].append(file_info)
                        result["total_files"] += 1

            return result

        except Exception as e:
            return {"error": f"Failed to index directory: {str(e)}"}

    def read_file_snippet(self, file_path: str, start_line: int = 1,
                         max_lines: int = 50) -> Dict[str, Any]:
        """Read a snippet from a text file"""
        if not self._is_path_allowed(file_path):
            return {"error": f"Access denied: {file_path}"}

        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        if not self._is_text_file(file_path):
            return {"error": f"Not a text file: {file_path}"}

        try:
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                return {"error": f"File too large: {file_size} bytes (max: {self.max_file_size})"}

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            total_lines = len(lines)
            end_line = min(start_line + max_lines - 1, total_lines)

            snippet_lines = lines[start_line-1:end_line]  # 0-indexed
            content = ''.join(snippet_lines)

            # Truncate if too long
            if len(content) > self.max_snippet_length:
                content = content[:self.max_snippet_length] + "..."

            return {
                "file_path": file_path,
                "start_line": start_line,
                "end_line": end_line,
                "total_lines": total_lines,
                "content": content,
                "truncated": len(''.join(snippet_lines)) > self.max_snippet_length
            }

        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}

    def search_files(self, query: str, path: str = ".",
                    file_extensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Search for text in files"""
        if not self._is_path_allowed(path):
            return {"error": f"Access denied: {path}"}

        try:
            results = []
            query_lower = query.lower()

            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)

                    # Check extension filter
                    if file_extensions:
                        if Path(file_path).suffix.lower() not in file_extensions:
                            continue

                    if not self._is_path_allowed(file_path) or not self._is_text_file(file_path):
                        continue

                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if query_lower in content.lower():
                                # Find line numbers
                                lines = content.split('\n')
                                matching_lines = []
                                for i, line in enumerate(lines, 1):
                                    if query_lower in line.lower():
                                        matching_lines.append({
                                            "line": i,
                                            "content": line.strip()
                                        })
                                        if len(matching_lines) >= 5:  # Limit matches per file
                                            break

                                results.append({
                                    "file_path": file_path,
                                    "matches": matching_lines
                                })

                    except Exception:
                        continue  # Skip files that can't be read

            return {"query": query, "results": results}

        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}

    def index(self, path: str = ".", max_depth: int = 2) -> Dict[str, Any]:
        """Simple index method for API compatibility"""
        result = self.index_directory(path, max_depth)
        if "error" in result:
            return result

        # Transform to match API expectations
        return {
            "files": [
                {
                    "path": f["path"],
                    "size": f["size"],
                    "type": "file" if f.get("is_text", True) else "file"
                }
                for f in result["files"]
            ],
            "total_files": result["total_files"],
            "total_dirs": result["total_dirs"]
        }