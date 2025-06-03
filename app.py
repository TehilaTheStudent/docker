import os
import flask
import requests
import logging
from functools import wraps
from werkzeug.security import safe_str_cmp

app = flask.Flask(__name__)

KUBE_API_URL = "https://kubernetes.default.svc"
TOKEN_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/token"
CA_CERT_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Load service account token
with open(TOKEN_PATH, "r") as f:
    TOKEN = f.read().strip()

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

# Auth credentials from environment
USERNAME = os.getenv("PROXY_USERNAME")
PASSWORD = os.getenv("PROXY_PASSWORD")

def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = flask.request.authorization
        if not auth or not safe_str_cmp(auth.username, USERNAME) or not safe_str_cmp(auth.password, PASSWORD):
            logging.warning("Unauthorized access attempt")
            return flask.Response(
                "Unauthorized", 401,
                {"WWW-Authenticate": "Basic realm=\"Login Required\""}
            )
        return func(*args, **kwargs)
    return wrapper

@app.route("/", methods=["GET"])
@require_auth
def index():
    return {"message": "Kubernetes API proxy is running"}, 200

@app.route("/<path:req_path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/api/<path:req_path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/apis/<path:req_path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@require_auth
def proxy(req_path=""):
    full_path = flask.request.path
    method = flask.request.method
    target_url = f"{KUBE_API_URL}{full_path}"

    logging.info(f"[{method}] {target_url}")

    try:
        resp = requests.request(
            method,
            target_url,
            headers=HEADERS,
            json=flask.request.get_json(silent=True),
            params=flask.request.args,
            verify=CA_CERT_PATH,
        )

        logging.info(f"→ {resp.status_code} {len(resp.content)} bytes")

        return flask.Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get("Content-Type", "application/json")
        )

    except Exception as e:
        logging.error(f"Request to {target_url} failed: {e}")
        return {"error": "Proxy request failed", "details": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
