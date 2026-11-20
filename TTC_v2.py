"""
====================================================================
TTC v2.0 Next-Gen — Interfaz GPU-Acelerada (Edge WebView2 + pywebview)
Coexiste en paralelo con TarkovScope.py (v1.5.1) compartiendo el 100%
de core/, DataStore RAM y tarkov_data.db sin riesgo de regresión.
====================================================================
"""
import functools
import http.server
import logging
import mimetypes
import os
import socketserver
import sys
import threading
import urllib.parse
from typing import Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import webview

from core.config import APP_VERSION, BUNDLE_DIR, CACHE_DIR
from core.database import init_db, is_db_populated
from core.datastore import get_datastore
from core.web_api import TTCWebAPI, resolve_web_asset_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TarkovScope.WebUI")


def _resolve_web_ui_dir() -> str:
    cand = os.path.join(BUNDLE_DIR, "web_ui")
    if os.path.isdir(cand):
        return cand
    return os.path.join(current_dir, "web_ui")


class _QuietThreadedTCPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class _TTCAssetHandler(http.server.BaseHTTPRequestHandler):
    web_ui_dir: str = ""

    def log_message(self, format: str, *args) -> None:
        return  # Silenciar logs de cada PNG en consola

    def _send_file(self, file_path: str, cache_max_age: int = 0) -> None:
        if not file_path or not os.path.isfile(file_path):
            self.send_error(404, "Not Found")
            return
        ctype, _ = mimetypes.guess_type(file_path)
        ctype = ctype or "application/octet-stream"
        try:
            with open(file_path, "rb") as f:
                data = f.read()
        except OSError:
            self.send_error(500, "Read Error")
            return

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        if cache_max_age > 0:
            self.send_header("Cache-Control", f"public, max-age={cache_max_age}")
        else:
            self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        rel = urllib.parse.unquote(parsed.path)

        if rel.startswith("/cache/"):
            asset_path = resolve_web_asset_path(rel[len("/cache/"):])
            self._send_file(asset_path or "", cache_max_age=86400)
            return

        if rel in ("", "/"):
            rel = "/index.html"

        clean_rel = rel.lstrip("/").replace("/", os.sep)
        target = os.path.realpath(os.path.join(self.web_ui_dir, clean_rel))
        root = os.path.realpath(self.web_ui_dir)
        try:
            if os.path.commonpath([target, root]) != root:
                self.send_error(403, "Forbidden")
                return
        except ValueError:
            self.send_error(403, "Forbidden")
            return

        self._send_file(target, cache_max_age=0)


def _start_local_server(web_ui_dir: str) -> tuple[_QuietThreadedTCPServer, str]:
    handler_cls = type(
        "_BoundTTCAssetHandler",
        (_TTCAssetHandler,),
        {"web_ui_dir": web_ui_dir},
    )
    httpd = _QuietThreadedTCPServer(("127.0.0.1", 0), handler_cls)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, f"http://127.0.0.1:{port}/index.html"


def _register_windows_appid() -> None:
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("TTC.TacticalTarkovCompanion.V2")
        except Exception:
            pass


def main() -> None:
    _register_windows_appid()
    init_db()
    if is_db_populated():
        get_datastore().ensure_loaded()

    web_ui_dir = _resolve_web_ui_dir()
    httpd, url = _start_local_server(web_ui_dir)

    window_holder: list[Optional[webview.Window]] = [None]

    def _set_topmost(enabled: bool) -> None:
        win = window_holder[0]
        if win is not None:
            win.on_top = bool(enabled)

    api = TTCWebAPI(on_toggle_topmost=_set_topmost)

    window = webview.create_window(
        title=f"TTC v{APP_VERSION} Next-Gen — Tactical Tarkov Companion",
        url=url,
        js_api=api,
        width=1440,
        height=900,
        min_size=(1160, 740),
        background_color="#090C12",
    )
    window_holder[0] = window

    wv_cache_dir = os.path.join(CACHE_DIR, "webview2_cache")
    os.makedirs(wv_cache_dir, exist_ok=True)
    try:
        webview.start(
            gui="edgechromium",
            debug=False,
            private_mode=False,
            storage_path=wv_cache_dir,
        )
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    main()
