import os
import flask
import requests

app = flask.Flask(__name__)

KUBE_API_URL = "https://kubernetes.default.svc"
TOKEN_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/token"
CA_CERT_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"

# Read token once on startup
with open(TOKEN_PATH, "r") as f:
    TOKEN = f.read().strip()

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

@app.route("/", methods=["GET"])
def index():
    return {"message": "Kubernetes API proxy is running"}, 200

@app.route("/<path:req_path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy(req_path):
    method = flask.request.method
    url = f"{KUBE_API_URL}/{req_path}"
    
    resp = requests.request(
        method,
        url,
        headers=HEADERS,
        json=flask.request.get_json(silent=True),
        params=flask.request.args,
        verify=CA_CERT_PATH,
    )

    return flask.Response(
        resp.content,
        status=resp.status_code,
        content_type=resp.headers.get("Content-Type", "application/json")
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
