/* Servidor estatico minimo para publicar la web en Railway.
   Sin dependencias: solo modulos incluidos en Node.
   La web en si es 100 % estatica; esto solo sirve los archivos. */
const http = require("http");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const ROOT = __dirname;
const PORT = process.env.PORT || 3000;

const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".mjs": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".webp": "image/webp",
  ".ico": "image/x-icon",
  ".txt": "text/plain; charset=utf-8",
  ".xml": "application/xml; charset=utf-8",
  ".wasm": "application/wasm",
  ".woff2": "font/woff2"
};

const COMPRESSIBLE = new Set([".html", ".css", ".js", ".mjs", ".json", ".svg", ".txt", ".xml"]);

/* Archivos de trabajo que no deben servirse */
const BLOCKED = [/^\/?\.htaccess$/i, /^\/?scripts\//i, /^\/?\.git/i, /^\/?package(-lock)?\.json$/i, /^\/?server\.js$/i];

function send(res, code, body, headers) {
  res.writeHead(code, Object.assign({ "X-Content-Type-Options": "nosniff" }, headers || {}));
  res.end(body);
}

const server = http.createServer((req, res) => {
  let urlPath;
  try {
    urlPath = decodeURIComponent(new URL(req.url, "http://x").pathname);
  } catch (e) {
    return send(res, 400, "Peticion incorrecta", { "Content-Type": "text/plain; charset=utf-8" });
  }

  if (urlPath.endsWith("/")) urlPath += "index.html";
  const rel = urlPath.replace(/^\/+/, "");

  if (BLOCKED.some((re) => re.test(rel))) {
    return send(res, 404, "No encontrado", { "Content-Type": "text/plain; charset=utf-8" });
  }

  const file = path.join(ROOT, rel);
  if (!file.startsWith(ROOT)) {
    return send(res, 403, "Prohibido", { "Content-Type": "text/plain; charset=utf-8" });
  }

  fs.stat(file, (err, st) => {
    if (err || !st.isFile()) {
      /* 404 con la propia pagina, para no perder al visitante */
      return fs.readFile(path.join(ROOT, "index.html"), (e2, html) => {
        if (e2) return send(res, 404, "No encontrado", { "Content-Type": "text/plain; charset=utf-8" });
        send(res, 404, html, { "Content-Type": TYPES[".html"] });
      });
    }

    const ext = path.extname(file).toLowerCase();
    const type = TYPES[ext] || "application/octet-stream";
    const longCache = /^(lib|assets)\//.test(rel) && ext !== ".html";
    const headers = {
      "Content-Type": type,
      "Cache-Control": longCache ? "public, max-age=2592000" : "public, max-age=0, must-revalidate",
      "Last-Modified": st.mtime.toUTCString()
    };

    const accepts = String(req.headers["accept-encoding"] || "");
    const gzip = COMPRESSIBLE.has(ext) && /\bgzip\b/.test(accepts);

    if (req.method === "HEAD") return send(res, 200, "", headers);

    const stream = fs.createReadStream(file);
    if (gzip) {
      headers["Content-Encoding"] = "gzip";
      headers["Vary"] = "Accept-Encoding";
      res.writeHead(200, headers);
      stream.pipe(zlib.createGzip()).pipe(res);
    } else {
      headers["Content-Length"] = st.size;
      res.writeHead(200, headers);
      stream.pipe(res);
    }
    stream.on("error", () => { try { res.destroy(); } catch (e) {} });
  });
});

server.listen(PORT, () => {
  console.log("QR3D escuchando en el puerto " + PORT);
});
