"""Run the sign recognizer on your phone.

The phone's browser does all the work (MediaPipe hand tracking, the classifier from
model.json, building words, speech). The laptop only serves the page and the model files
over HTTPS on the local Wi-Fi. Phone and laptop must be on the same Wi-Fi.

    python serve.py [--port 8443] [--model model.json]

Phone browsers only allow the camera over HTTPS, so a self-signed certificate is made in
certs/ on first run (needs the openssl command). The phone warns about it once: choose
"Advanced" -> "Proceed".
"""
import argparse, ipaddress, json, os, socket, ssl, subprocess, sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from common import ROOT, CLASSIFIER_PATH, ensure_landmarker_model

WEB_DIR = os.path.join(ROOT, "web")
CERT_DIR = os.path.join(ROOT, "certs")


def make_handler(model_path, landmarker_path):
    # URL path -> (file, content type, cache-control). Nothing else is served.
    routes = {
        "/": (os.path.join(WEB_DIR, "index.html"), "text/html; charset=utf-8", "no-cache"),
        "/index.html": (os.path.join(WEB_DIR, "index.html"), "text/html; charset=utf-8", "no-cache"),
        "/app.js": (os.path.join(WEB_DIR, "app.js"), "text/javascript; charset=utf-8", "no-cache"),
        "/model.json": (model_path, "application/json", "no-store"),
        "/hand_landmarker.task": (landmarker_path, "application/octet-stream", "max-age=86400"),
    }

    class Handler(BaseHTTPRequestHandler):
        timeout = 30   # drop idle or stuck connections

        def log_message(self, *args):
            pass

        def send(self, code, body, ctype, cache="no-store", head=False):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", cache)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            if not head:
                self.wfile.write(body)

        def _serve(self, head):
            path = urlparse(self.path).path
            if path not in routes:
                return self.send(404, b'{"error": "not found"}', "application/json", head=head)
            file, ctype, cache = routes[path]
            try:
                with open(file, "rb") as f:
                    body = f.read()
            except OSError:
                if path == "/model.json":
                    msg = {"error": "model.json not found. Train first: run train.py on the laptop."}
                else:
                    msg = {"error": "%s is missing on the laptop" % path}
                return self.send(404, json.dumps(msg).encode(), "application/json", head=head)
            self.send(200, body, ctype, cache, head=head)

        def do_GET(self):
            self._serve(head=False)

        def do_HEAD(self):
            self._serve(head=True)

    return Handler


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        # Phones drop connections and reject the self-signed certificate until the user
        # accepts it; those are normal, not worth a traceback.
        if not isinstance(sys.exc_info()[1], (ssl.SSLError, ConnectionError, TimeoutError, socket.timeout)):
            super().handle_error(request, client_address)


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))   # no packet is sent; this only picks the outgoing interface
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def ensure_cert(ip):
    """Self-signed certificate in certs/. Made again if the laptop's LAN IP changed."""
    crt, key, ip_file = (os.path.join(CERT_DIR, n) for n in ("cert.pem", "key.pem", "ip.txt"))
    if os.path.exists(crt) and os.path.exists(key):
        try:
            with open(ip_file) as f:
                if f.read().strip() == ip:
                    return crt, key
        except OSError:
            pass
    os.makedirs(CERT_DIR, exist_ok=True)
    san = "subjectAltName=DNS:localhost,IP:127.0.0.1"
    try:
        ipaddress.ip_address(ip)
        if ip != "127.0.0.1":
            san += ",IP:" + ip
    except ValueError:
        pass
    try:
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "825",
                        "-keyout", key, "-out", crt, "-subj", "/CN=sign-language-phone", "-addext", san],
                       check=True, capture_output=True)
    except FileNotFoundError:
        raise SystemExit("ERROR: the 'openssl' command is needed to make an HTTPS certificate "
                         "(Ubuntu: sudo apt install openssl).")
    except subprocess.CalledProcessError as e:
        raise SystemExit("ERROR: openssl failed: %s" % e.stderr.decode(errors="replace").strip())
    with open(ip_file, "w") as f:
        f.write(ip + "\n")
    return crt, key


def main():
    parser = argparse.ArgumentParser(description="Serve the phone version (the phone does the recognition).")
    parser.add_argument("--port", type=int, default=8443)
    parser.add_argument("--host", default="0.0.0.0", help="address to listen on (default: all)")
    parser.add_argument("--model", default=CLASSIFIER_PATH, help="classifier made by train.py (default: model.json)")
    args = parser.parse_args()

    model_path = os.path.abspath(args.model)
    landmarker_path = ensure_landmarker_model()
    ip = lan_ip()
    crt, key = ensure_cert(ip)
    try:
        server = Server((args.host, args.port), make_handler(model_path, landmarker_path))
    except OSError as e:
        raise SystemExit("ERROR: cannot listen on port %d (%s). Try another --port." % (args.port, e.strerror))
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(crt, key)
    # Handshake lazily in the request thread, so a slow phone can't block the accept loop.
    server.socket = ctx.wrap_socket(server.socket, server_side=True, do_handshake_on_connect=False)

    print("\nOn your phone (same Wi-Fi as this laptop), open:\n\n    https://%s:%d\n" % (ip, args.port))
    print("1. The phone warns 'connection not private' (self-signed certificate):")
    print("   tap Advanced -> Proceed (Safari: Show Details -> visit this website).")
    print("2. Tap Start and allow camera access.")
    if not os.path.exists(model_path):
        print("\nWARNING: %s not found. Train first: run train.py, then reload the page." % model_path)
    else:
        print("\nClassifier: %s" % model_path)
    print("Press Ctrl+C here to stop.\n")
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("Stopped.")


if __name__ == "__main__":
    main()
