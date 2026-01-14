import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .engine import build_vectors, kmeans, top_terms

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "docs.json"
WEB_DIR = BASE_DIR / "web"


def load_docs():
    if not DATA_PATH.exists():
        return []
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def save_docs(docs):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(docs, indent=2), encoding="utf-8")


def seed_docs():
    docs = [
        {"id": 1, "title": "Model ops", "body": "monitor drift, alerts, and model registry"},
        {"id": 2, "title": "Design system", "body": "tokens, typography, and layout patterns"},
        {"id": 3, "title": "Prompting", "body": "few-shot, chain of thought, prompt templates"},
        {"id": 4, "title": "Sales playbook", "body": "discovery calls, pipeline, and forecasting"},
        {"id": 5, "title": "Data pipeline", "body": "ingest events, clean data, build features"},
        {"id": 6, "title": "Marketing launch", "body": "positioning, landing pages, and campaigns"},
        {"id": 7, "title": "QA checklist", "body": "test coverage, regression, automation"},
        {"id": 8, "title": "Deployment", "body": "infrastructure, canary releases, rollback"},
    ]
    save_docs(docs)
    return docs


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def log_message(self, format, *args):
        return

    def _send_json(self, payload, status=HTTPStatus.OK):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        body = self.rfile.read(length)
        return json.loads(body.decode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/cluster":
            payload = self._read_json()
            k = int(payload.get("k", 3))
            docs = load_docs()
            vectors = build_vectors(docs)
            assignments, centroids = kmeans(vectors, k)
            clusters = {i: {"docs": [], "terms": top_terms(centroids[i])} for i in range(k)}
            for idx, doc in enumerate(docs):
                clusters[assignments[idx]]["docs"].append(doc)
            self._send_json({"clusters": clusters})
            return
        if parsed.path == "/api/seed":
            docs = seed_docs()
            self._send_json({"count": len(docs)})
            return
        self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        super().do_GET()


def run(host="127.0.0.1", port=5173):
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"TopicAtlas running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run TopicAtlas")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5173)
    args = parser.parse_args()

    run(host=args.host, port=args.port)
