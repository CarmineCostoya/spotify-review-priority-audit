from __future__ import annotations

import json
import mimetypes
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


class DashboardHandler(BaseHTTPRequestHandler):
    database = "outputs/spotify_audit.db"
    static_dir = Path("dashboard")

    def _json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith("/api/"):
            return self._api(path)
        file = self.static_dir / ("index.html" if path == "/" else path.lstrip("/"))
        if not file.exists() or not file.is_file():
            return self._json({"error": "not found"}, 404)
        body = file.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(file.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def _api(self, path):
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        try:
            if path == "/api/health":
                return self._json({"status": "ok", "database": self.database})
            if path == "/api/metrics":
                rows = connection.execute("SELECT status, COUNT(*) count FROM reviews GROUP BY status").fetchall()
                topics = connection.execute("SELECT topic, COUNT(*) count FROM reviews WHERE status='completed' GROUP BY topic ORDER BY count DESC").fetchall()
                return self._json({"statuses": [dict(r) for r in rows], "topics": [dict(r) for r in topics]})
            if path == "/api/issues":
                rows = connection.execute("SELECT * FROM ranking ORDER BY rank").fetchall()
                return self._json([dict(r) for r in rows])
            if path.startswith("/api/issues/"):
                issue = path.split("/")[-1]
                rows = connection.execute("SELECT r.review_id,r.review_text,r.severity,r.intent FROM reviews r JOIN issue_membership m USING(review_id) WHERE m.issue_id=? LIMIT 25", (issue,)).fetchall()
                return self._json({"issue_id": issue, "reviews": [dict(r) for r in rows]})
            if path.startswith("/api/reviews/"):
                rid = path.split("/")[-1]
                row = connection.execute("SELECT * FROM reviews WHERE review_id=?", (rid,)).fetchone()
                return self._json(dict(row) if row else {"error": "not found"}, 200 if row else 404)
            return self._json({"error": "not found"}, 404)
        finally:
            connection.close()


def serve(database: str, port: int):
    DashboardHandler.database = database
    server = ThreadingHTTPServer(("127.0.0.1", port), DashboardHandler)
    print(f"Dashboard available at http://127.0.0.1:{port}")
    server.serve_forever()

