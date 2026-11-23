"""three.js stand-in for LeoCAD: renders the kit's base / id / solo pictures in headless Chromium.
Same camera maths as mockit.render.Camera (LDraw coordinates, -Y up, vertical fov)."""
import os, base64, threading, functools, http.server, socketserver, json
from playwright.sync_api import sync_playwright

SRV = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'srv')

class _Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

def _serve(port):
    h = functools.partial(_Q, directory=SRV)
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    httpd = socketserver.ThreadingTCPServer(('127.0.0.1', port), h); httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd

class Renderer:
    def __init__(self, port=0):
        self.httpd = _serve(port); port = self.httpd.server_address[1]
        self.pw = sync_playwright().start()
        self.br = self.pw.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        self.pg = self.br.new_page(viewport={'width': 400, 'height': 300})
        self.pg.goto(f'http://127.0.0.1:{port}/index.html')
        self.pg.wait_for_function('window.ready === true', timeout=120000)

    def job(self, j):
        r = self.pg.evaluate('j => window.renderJob(j)', j)
        dec = lambda u: base64.b64decode(u.split(',', 1)[1])
        return dec(r['main']), [dec(u) for u in r.get('solos', [])]

    def thumb(self, part, color, edge, size):
        r = self.pg.evaluate('j => window.fitJob(j)', dict(part=part, color=color, edge=edge, W=size, H=size, lat=30, lon=45))
        return base64.b64decode(r['main'].split(',', 1)[1])

    def close(self):
        self.br.close(); self.pw.stop()
