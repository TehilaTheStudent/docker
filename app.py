import os
import flask
import requests
import logging

app = flask.Flask(__name__)

KUBE_API_URL = "https://kubernetes.default.svc"
TOKEN_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/token"
CA_CERT_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Load token at startup
with open(TOKEN_PATH, "r") as f:
    TOKEN = f.read().strip()

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

# Load allowed IPs from env
ALLOWED_IPS = os.getenv("ALLOWED_IPS", "").split(",")

def get_client_ip():
    forwarded_for = flask.request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return flask.request.remote_addr

@app.before_request
def restrict_ip():
    ip = get_client_ip()
    if ip not in ALLOWED_IPS:
        logging.warning(f"Blocked IP: {ip}")
        return {"error": "Access denied"}, 403
    logging.info(f"Allowed IP: {ip}")

@app.route("/", methods=["GET"])
def index():
    return {"message": "Kubernetes API proxy is running"}, 200

@app.route("/<path:req_path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/api/<path:req_path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/apis/<path:req_path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
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
