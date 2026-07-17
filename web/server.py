from __future__ import annotations

import argparse
import json
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


PACKAGE_DIR = Path(__file__).resolve().parents[1]
PLUGINS_DIR = PACKAGE_DIR.parent
if str(PLUGINS_DIR) not in sys.path:
    sys.path.insert(0, str(PLUGINS_DIR))

from astrbot_plugin_jinyong_rogue.web_runtime import LocalWebGameRuntime


STATIC_DIR = Path(__file__).resolve().parent / "static"
DATA_DIR = PACKAGE_DIR / "data" / "web"


class JinyongWebHandler(SimpleHTTPRequestHandler):
    runtime = LocalWebGameRuntime(DATA_DIR)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_POST(self) -> None:
        if self.path != "/api/command":
            self.send_error(404)
            return
        payload = self._read_json()
        result = self.runtime.dispatch(
            str(payload.get("userId") or "web-tester"),
            str(payload.get("nickname") or "Web Tester"),
            str(payload.get("text") or ""),
        )
        self._write_json(result)

    def do_GET(self) -> None:
        if self.path.startswith("/cards/"):
            self._serve_card()
            return
        super().do_GET()

    def _serve_card(self) -> None:
        request_path = urlparse(self.path).path
        name = Path(unquote(request_path.removeprefix("/cards/"))).name
        path = self.runtime.card_dir / name
        if not path.exists() or path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/png" if path.suffix.lower() == ".png" else "image/jpeg")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(path.stat().st_size))
        self.end_headers()
        with path.open("rb") as fh:
            self.wfile.write(fh.read())

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or "0")
        raw = self.rfile.read(length)
        if not raw:
            return {}
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}

    def _write_json(self, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="金庸踢门团本地 Web 调试服务器")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8790)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), JinyongWebHandler)
    print(f"Web test server: http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
