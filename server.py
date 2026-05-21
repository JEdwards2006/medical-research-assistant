"""
Medical Research Assistant - Local Server
Run this file with Python. It starts a local web server at http://localhost:8000
and proxies requests to NCBI and Anthropic so the browser can reach them.
"""

import http.server
import urllib.error
import urllib.request
import urllib.parse
import json
import os
import sys
from datetime import datetime

PORT = 8000
STATIC_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(STATIC_DIR, "app.log")
LOG_MAX_LINES = 10000


class RollingLogger:
    def __init__(self, filepath, max_lines=10000):
        self.filepath = filepath
        self.max_lines = max_lines

    def write(self, message):
        """Append a line to the log file, trimming if necessary."""
        try:
            lines = []
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            
            # Add new line with timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_line = f"[{timestamp}] {message}\n"
            lines.append(new_line)
            
            # Trim to max_lines, keeping the most recent
            if len(lines) > self.max_lines:
                lines = lines[-self.max_lines:]
            
            # Write back
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        except Exception as e:
            print(f"[LOG ERROR] {e}", flush=True)


logger = RollingLogger(LOG_FILE, LOG_MAX_LINES)


class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        msg = f"{args[0]} {args[1]}" if len(args) > 1 else str(args[0])
        print(f"  {msg}", flush=True)
        logger.write(msg)

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, x-api-key, anthropic-version")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # Proxy NCBI requests
        if parsed.path.startswith("/ncbi/"):
            ncbi_path = parsed.path[len("/ncbi"):]
            target = f"https://eutils.ncbi.nlm.nih.gov{ncbi_path}"
            if parsed.query:
                target += f"?{parsed.query}"
            try:
                req = urllib.request.Request(target, headers={
                    "User-Agent": "python-medical-research-assistant/1.0"
                })
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = resp.read()
                    ct = resp.headers.get("Content-Type", "application/json")
                self.send_response(200)
                self.send_header("Content-Type", ct)
                self.send_cors()
                self.end_headers()
                self.wfile.write(data)
            except urllib.error.HTTPError as e:
                err_body = e.read()
                err_msg = f"NCBI proxy HTTPError {e.code}: {err_body[:200]}"
                print(f"  {err_msg}", flush=True)
                logger.write(err_msg)
                self.send_response(e.code)
                self.send_header("Content-Type", e.headers.get("Content-Type", "application/json"))
                self.send_cors()
                self.end_headers()
                self.wfile.write(err_body)
            except Exception as e:
                err_msg = f"NCBI proxy exception: {e}"
                print(f"  {err_msg}", flush=True)
                logger.write(err_msg)
                self._error(502, str(e))
            return

        # Serve static files
        if parsed.path == "/" or parsed.path == "":
            filepath = os.path.join(STATIC_DIR, "index.html")
        else:
            filepath = os.path.join(STATIC_DIR, parsed.path.lstrip("/"))

        if os.path.isfile(filepath):
            ext = os.path.splitext(filepath)[1]
            ct = {"html": "text/html", "js": "application/javascript",
                  "css": "text/css"}.get(ext.lstrip("."), "text/plain")
            with open(filepath, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", ct)
            self.send_cors()
            self.end_headers()
            self.wfile.write(data)
        else:
            self._error(404, "Not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        # Accept log entries from browser
        if path == "/log":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                msg = data.get("message", "")
                if msg:
                    logger.write(f"[browser] {msg}")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                self._error(400, str(e))
            return

        # Proxy Anthropic API
        if path == "/anthropic":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            api_key = self.headers.get("x-api-key", "")
            print(f"  Forwarding to Anthropic API (key: {'set' if api_key else 'MISSING'})", flush=True)
            try:
                req = urllib.request.Request(
                    "https://api.anthropic.com/v1/messages",
                    data=body,
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01"
                    },
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(data)
                print(f"  Anthropic API: success", flush=True)
            except urllib.error.HTTPError as e:
                err_body = e.read()
                err_msg = f"Anthropic API error {e.code}: {err_body[:200]}"
                print(f"  {err_msg}", flush=True)
                logger.write(err_msg)
                self.send_response(e.code)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(err_body)
            except Exception as e:
                err_msg = f"Anthropic proxy exception: {e}"
                print(f"  {err_msg}", flush=True)
                logger.write(err_msg)
                self._error(502, str(e))
            return

        print(f"  POST {path} -> 404 (unrecognized route)", flush=True)
        logger.write(f"POST {path} -> 404 (unrecognized route)")
        self._error(404, "Not found")

    def _error(self, code, msg):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_cors()
        self.end_headers()
        self.wfile.write(json.dumps({"error": msg}).encode())


if __name__ == "__main__":
    server = http.server.HTTPServer(("localhost", PORT), Handler)
    print(f"\n{'='*50}")
    print(f"  Medical Research Assistant is running!")
    print(f"  Open your browser and go to:")
    print(f"  http://localhost:{PORT}")
    print(f"{'='*50}")
    print(f"\n  (Keep this window open while you use the tool)")
    print(f"  (Close this window when you are done)")
    print(f"  (Log file: {LOG_FILE})\n")
    logger.write("=== Server started ===")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped. Goodbye!")
        logger.write("=== Server stopped ===")
