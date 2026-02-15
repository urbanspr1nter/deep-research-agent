from smolagents.tools import Tool


class FileSystemTool(Tool):
    name = "file_system"
    description = """Performs file system operations within a sandboxed directory. All paths you provide are relative to the sandbox root. You have full freedom to create, read, modify, organize, and delete any files and directories within the sandbox. You cannot access anything outside of it.

Operations and expected args:
- listdir — args: ["path"] — Lists all files and directories at the given path. Use ["."] for the sandbox root.
- read — args: ["path"] — Reads and returns the full text content (UTF-8) of a file.
- write — args: ["path", "content"] — Creates or overwrites a file with the given text content. Parent directories are created automatically.
- append — args: ["path", "content"] — Appends text content to the end of an existing file.
- delete — args: ["path"] — Deletes a single file.
- copy — args: ["source", "destination"] — Copies a file or directory to a new location within the sandbox.
- move — args: ["source", "destination"] — Moves or renames a file or directory within the sandbox.
- mkdir — args: ["path"] — Creates a directory, including any necessary parent directories.
- rmdir — args: ["path"] — Recursively removes a directory and all of its contents. Cannot remove the sandbox root itself.
- download — args: ["url", "path"] — Downloads a file from a URL and saves it to the given path in the sandbox. Useful for fetching PDFs, images, or other files from the web."""
    inputs = {
        "type": {
            "type": "string",
            "description": "The operation to perform. One of: listdir, read, write, append, delete, copy, move, mkdir, rmdir, download"
        },
        "args": {
            "type": "array",
            "description": "List of string arguments for the operation. The meaning of each element depends on the operation type — see the tool description for details."
        }
    }
    output_type = "string"

    def __init__(self, sandbox_root: str = ""):
        super().__init__()

        import os

        self.sandbox_root = os.path.realpath(
            sandbox_root or os.path.join(os.path.expanduser("~"), "sandbox")
        )
        os.makedirs(self.sandbox_root, exist_ok=True)

        # Let the LLM know the actual sandbox path
        self.description = f"{self.description}\n\nThe sandbox root directory is: {self.sandbox_root}"

    def _resolve_and_validate(self, path: str) -> str:
        """Resolve a path relative to the sandbox root and ensure it stays within the sandbox."""
        import os

        # Strip leading slashes so the path is always treated as relative
        path = path.lstrip("/")
        resolved = os.path.realpath(os.path.join(self.sandbox_root, path))

        if not resolved.startswith(self.sandbox_root):
            raise ValueError(f"Access denied: path '{path}' resolves outside the sandbox.")

        return resolved

    def _human_size(self, size) -> str:
        for unit in ["B", "KB", "MB"]:
            if size < 1024:
                return f"{size:.1f}{unit}" if unit != "B" else f"{size}{unit}"
            size = size / 1024
        return f"{size:.1f}GB"

    def forward(self, type: str, args: list) -> str:
        import os
        import shutil

        try:
            if type == "listdir":
                if len(args) < 1:
                    return "Error: listdir requires args: [path]"
                resolved = self._resolve_and_validate(args[0])
                if not os.path.isdir(resolved):
                    return f"Error: '{args[0]}' is not a directory."
                entries = []
                for entry in sorted(os.listdir(resolved)):
                    full_path = os.path.join(resolved, entry)
                    if os.path.isdir(full_path):
                        entries.append(f"[DIR]  {entry}")
                    else:
                        size = os.path.getsize(full_path)
                        entries.append(f"[FILE] {entry} ({self._human_size(size)})")
                if not entries:
                    return "(empty directory)"
                return "\n".join(entries)

            elif type == "read":
                if len(args) < 1:
                    return "Error: read requires args: [path]"
                resolved = self._resolve_and_validate(args[0])
                if not os.path.isfile(resolved):
                    return f"Error: '{args[0]}' is not a file."
                with open(resolved, "r", encoding="utf-8") as f:
                    return f.read()

            elif type == "write":
                if len(args) < 2:
                    return "Error: write requires args: [path, content]"
                resolved = self._resolve_and_validate(args[0])
                os.makedirs(os.path.dirname(resolved), exist_ok=True)
                with open(resolved, "w", encoding="utf-8") as f:
                    written = f.write(args[1])
                return f"Written {self._human_size(written)} to {args[0]}"

            elif type == "append":
                if len(args) < 2:
                    return "Error: append requires args: [path, content]"
                resolved = self._resolve_and_validate(args[0])
                if not os.path.isfile(resolved):
                    return f"Error: '{args[0]}' does not exist. Use 'write' to create a new file."
                with open(resolved, "a", encoding="utf-8") as f:
                    written = f.write(args[1])
                return f"Appended {self._human_size(written)} to {args[0]}"

            elif type == "delete":
                if len(args) < 1:
                    return "Error: delete requires args: [path]"
                resolved = self._resolve_and_validate(args[0])
                if not os.path.isfile(resolved):
                    return f"Error: '{args[0]}' is not a file."
                os.remove(resolved)
                return f"Deleted {args[0]}"

            elif type == "copy":
                if len(args) < 2:
                    return "Error: copy requires args: [source, destination]"
                src = self._resolve_and_validate(args[0])
                dst = self._resolve_and_validate(args[1])
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
                return f"Copied {args[0]} to {args[1]}"

            elif type == "move":
                if len(args) < 2:
                    return "Error: move requires args: [source, destination]"
                src = self._resolve_and_validate(args[0])
                dst = self._resolve_and_validate(args[1])
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(src, dst)
                return f"Moved {args[0]} to {args[1]}"

            elif type == "mkdir":
                if len(args) < 1:
                    return "Error: mkdir requires args: [path]"
                resolved = self._resolve_and_validate(args[0])
                os.makedirs(resolved, exist_ok=True)
                return f"Created directory {args[0]}"

            elif type == "rmdir":
                if len(args) < 1:
                    return "Error: rmdir requires args: [path]"
                resolved = self._resolve_and_validate(args[0])
                if not os.path.isdir(resolved):
                    return f"Error: '{args[0]}' is not a directory."
                if resolved == self.sandbox_root:
                    return "Error: Cannot remove the sandbox root directory."
                shutil.rmtree(resolved)
                return f"Removed directory {args[0]} and all its contents"

            elif type == "download":
                if len(args) < 2:
                    return "Error: download requires args: [url, path]"
                import requests
                resolved = self._resolve_and_validate(args[1])
                os.makedirs(os.path.dirname(resolved), exist_ok=True)
                response = requests.get(args[0], timeout=120)
                response.raise_for_status()
                with open(resolved, "wb") as f:
                    f.write(response.content)
                return f"Downloaded {self._human_size(len(response.content))} from {args[0]} to {args[1]}"

            else:
                return f"Error: Unknown operation '{type}'. Must be one of: listdir, read, write, append, delete, copy, move, mkdir, rmdir, download"

        except ValueError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error: {type} failed — {e}"
