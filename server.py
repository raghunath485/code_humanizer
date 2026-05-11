from __future__ import annotations

import json
import mimetypes
import traceback
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from humanizer import HumanizeOptions, humanize

# Resolve the project root directory
ROOT = Path(__file__).parent.resolve()
MAX_REQUEST_SIZE = 1024 * 1024


class HumanizerHandler(BaseHTTPRequestHandler):
    """HTTP handler for the Code Humanizer service.

    Supports GET requests for static files and a POST endpoint
    ``/api/humanize`` that receives code and formatting options.
    """

    def do_GET(self) -> None:
        """Serve static files from the project root.

        The root URL (``/``) is mapped to ``/index.html``.
        """
        parsed = urlparse(self.path)
        request_path = parsed.path
        if request_path == "/":
            request_path = "/index.html"
        self.serve_static(request_path)

    def do_POST(self) -> None:
        """Handle ``/api/humanize`` POST requests.

        Expected JSON payload::

            {
                "code": "...",
                "options": { ... }
            }
        """
        parsed = urlparse(self.path)
        if parsed.path != "/api/humanize":
            self.send_error(HTTPStatus.NOT_FOUND, "Route not found")
            return
        # Read request body size and enforce limit
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length > MAX_REQUEST_SIZE:
            self.send_json({"error": "Request too large"}, status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return
        raw_body = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_body or b"{}")
        except json.JSONDecodeError:
            self.send_json({"error": "Invalid JSON payload."}, status=HTTPStatus.BAD_REQUEST)
            return
        # Extract options with sensible defaults
        options = payload.get("options", {})
        settings = HumanizeOptions(
            add_summary_comment=bool(options.get("add_summary_comment", True)),
            rename_identifiers=bool(options.get("rename_identifiers", True)),
            normalize_spacing=bool(options.get("normalize_spacing", True)),
            language_hint=str(options.get("language_hint", "auto")),
            target_profile=str(options.get("target_profile", "developer_friendly")),
            add_docstrings=bool(options.get("add_docstrings", True)),
            explain_complexity=bool(options.get("explain_complexity", True)),
            detect_dead_code=bool(options.get("detect_dead_code", True)),
        )
        try:
            result = humanize(str(payload.get("code", "")), settings)
            self.send_json(result)
        except Exception as error:
            traceback.print_exc()
            self.send_json({"error": str(error), "status": "internal_error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def serve_static(self, request_path: str) -> None:
        """Serve a static file from the project directory.

        Security checks ensure the requested path stays within ``ROOT``.
        """
        safe_path = Path(unquote(request_path.lstrip("/")))
        file_path = (ROOT / safe_path).resolve()
        # Prevent path traversal attacks
        if ROOT not in file_path.parents and file_path != ROOT:
            self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
            return
        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return
        content_type, _ = mimetypes.guess_type(file_path.name)
        payload = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(payload)

    def send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        """Utility to send JSON responses.

        ``payload`` is any JSON‑serialisable object.
        """
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args) -> None:
        """Suppress default request logging to keep console output clean."""
        return


def run() -> None:
    host = "127.0.0.1"
    port = 8000
    server = ThreadingHTTPServer((host, port), HumanizerHandler)
    print(f"Server running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
