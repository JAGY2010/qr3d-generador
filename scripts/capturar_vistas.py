#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
capturar_vistas.py - servidor de desarrollo para generar las imagenes del sitio.

Sirve la web en http://127.0.0.1:8145 y ademas acepta:

    POST /guardar   {"nombre": "algo.png", "datos": "data:image/png;base64,..."}

para que la propia pagina pueda escribir en assets/. Se usa para capturar las
vistas 3D de las piezas (imagenes propias, generadas con el mismo motor que ve
el visitante) y para guardar los archivos de ejemplo descargables.

NO se despliega: es una herramienta de desarrollo. Ejecutar desde la raiz.
"""
import base64
import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.getcwd()
PORT = 8145
PERMITIDOS = ("assets/img/", "assets/descargas/")


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        if self.path != "/guardar":
            self.send_error(404)
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n).decode("utf-8"))
            nombre = payload["nombre"].replace("\\", "/").lstrip("/")
            if not nombre.startswith(PERMITIDOS) or ".." in nombre:
                raise ValueError("ruta no permitida: " + nombre)

            datos = payload["datos"]
            if "," in datos:
                datos = datos.split(",", 1)[1]
            crudo = base64.b64decode(datos)

            destino = os.path.join(ROOT, nombre)
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            with open(destino, "wb") as f:
                f.write(crudo)
            print("  [guardado] %-46s %7d bytes" % (nombre, len(crudo)))

            cuerpo = json.dumps({"ok": True, "bytes": len(crudo)}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)
        except Exception as e:
            print("  [ERROR] %s" % e)
            self.send_error(400, str(e))


if __name__ == "__main__":
    print("Sirviendo %s en http://127.0.0.1:%d  (Ctrl+C para parar)" % (ROOT, PORT))
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
