"""SciSolve — Scientific Computing Assistant (Flask entry point).

Run with:  python app.py   ->  http://127.0.0.1:5000
"""
from flask import Flask, jsonify, render_template, request

from backend import router

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # questions are short; reject huge bodies


@app.get("/")
def index():
    # Module metadata is rendered into the page so the sidebar, cards and
    # landing page all come from a single source: the backend modules.
    return render_template("index.html", modules=router.list_modules())


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/solve")
def solve():
    payload = request.get_json(silent=True) or {}
    module_id = str(payload.get("module", ""))
    query = str(payload.get("query", ""))
    result, http_status = router.solve(module_id, query)
    return jsonify(result), http_status


@app.errorhandler(413)
def too_large(_error):
    return jsonify({"status": "error", "message": "That request is too large."}), 413


if __name__ == "__main__":
    # debug=True is for local development only. Turn it off before deploying.
    import os

app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 5000)),
    debug=False
)
