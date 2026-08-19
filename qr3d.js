/* =============================================================
   qr3d.js - motor del objeto 3D
   - Convierte la imagen del codigo (mascara en blanco y negro) en relieve.
   - Construye base (soporte / llavero / placa) + relieve como DOS mallas.
   - Exporta 3MF (dos colores dentro del archivo) y STL (zip de dos piezas).
   - Vista previa con three.js, cargado de forma perezosa.

   Todo son numeros en milimetros. Eje Z hacia arriba, origen en la esquina
   minima de la pieza (todo en el octante positivo, como piden los slicers).

   Unico global: window.__QR3D__
   ============================================================= */
(function () {
  "use strict";

  var THREE = null;
  var OrbitControls = null;
  var enginePromise = null;

  /* ---------------------------------------------------------------
     Carga perezosa de three.js (mapa de importaciones en el <head>)
     --------------------------------------------------------------- */
  function loadEngine() {
    if (enginePromise) return enginePromise;
    enginePromise = Promise.all([
      /* dynamic import desde un script clasico: el puente ESM de la skill */
      import("three"),
      import("three/addons/controls/OrbitControls.js")
    ]).then(function (mods) {
      THREE = mods[0];
      OrbitControls = mods[1].OrbitControls;
      return THREE;
    });
    return enginePromise;
  }

  function hasWebGL() {
    try {
      var c = document.createElement("canvas");
      return !!(window.WebGLRenderingContext &&
        (c.getContext("webgl2") || c.getContext("webgl") || c.getContext("experimental-webgl")));
    } catch (e) { return false; }
  }

  /* ---------------------------------------------------------------
     Geometria basica: cajas a mano (sopa de triangulos, sin indices)
     --------------------------------------------------------------- */
  function pushBox(a, x, y, z, w, h, d) {
    var x1 = x + w, y1 = y + h, z1 = z + d;
    /* 6 caras x 2 triangulos x 3 vertices */
    var v = [
      /* z- */ x,y,z,  x1,y1,z,  x1,y,z,   x,y,z,  x,y1,z,  x1,y1,z,
      /* z+ */ x,y,z1, x1,y,z1, x1,y1,z1,  x,y,z1, x1,y1,z1, x,y1,z1,
      /* y- */ x,y,z,  x1,y,z1, x,y,z1,    x,y,z,  x1,y,z,  x1,y,z1,
      /* y+ */ x,y1,z, x,y1,z1, x1,y1,z1,  x,y1,z, x1,y1,z1, x1,y1,z,
      /* x- */ x,y,z,  x,y1,z1, x,y1,z,    x,y,z,  x,y,z1,  x,y1,z1,
      /* x+ */ x1,y,z, x1,y1,z, x1,y1,z1,  x1,y,z, x1,y1,z1, x1,y,z1
    ];
    for (var i = 0; i < v.length; i++) a.push(v[i]);
  }

  /* Fusiona celdas encendidas en el menor numero de rectangulos maximos.
     Sin esto, un codigo de 33 modulos generaria cientos de miles de cajas. */
  function gridRects(on, cols, rows) {
    var used = new Uint8Array(cols * rows);
    var out = [];
    for (var r = 0; r < rows; r++) {
      for (var c = 0; c < cols; c++) {
        if (used[r * cols + c] || !on(r, c)) continue;
        var w = 1;
        while (c + w < cols && !used[r * cols + c + w] && on(r, c + w)) w++;
        var h = 1;
        grow: while (r + h < rows) {
          for (var k = 0; k < w; k++) {
            if (used[(r + h) * cols + c + k] || !on(r + h, c + k)) break grow;
          }
          h++;
        }
        for (var rr = r; rr < r + h; rr++) {
          for (var cc = c; cc < c + w; cc++) used[rr * cols + cc] = 1;
        }
        out.push({ c: c, r: r, w: w, h: h });
      }
    }
    return out;
  }

  /* ---------------------------------------------------------------
     Distribucion de la cara: cuanto mide cada cosa en milimetros
     --------------------------------------------------------------- */
  function layout(format, W, moduleCount, hasText) {
    var B = window.__BRAND__ || {};
    var cfg = (B.formats || {})[format] || {};
    var topBand = cfg.topBand || 0;

    /* Zona tranquila obligatoria: 4 modulos por cada lado.
       quiet = 4 * (W - 2*quiet) / n  ->  quiet = 4W / (n + 8) */
    var quiet = (4 * W) / (moduleCount + 8);
    if (quiet < 3) quiet = 3;
    if (quiet > W * 0.18) quiet = W * 0.18;

    var qrSize = W - 2 * quiet;
    var moduleMm = qrSize / moduleCount;

    var textH = hasText ? Math.min(12, Math.max(5, W * 0.115)) : 0;
    var gap = hasText ? Math.max(1.8, W * 0.03) : 0;

    var H = quiet + topBand + qrSize + gap + textH + quiet;

    return {
      W: W, H: H, quiet: quiet, topBand: topBand,
      qrSize: qrSize, moduleMm: moduleMm,
      qrX: quiet,
      qrY: quiet + textH + gap,               /* medido desde abajo */
      textX: quiet, textY: quiet,
      textW: W - 2 * quiet, textH: textH
    };
  }

  /* ---------------------------------------------------------------
     Perfiles de la base
     --------------------------------------------------------------- */
  function roundedRectShape(W, H, r) {
    var s = new THREE.Shape();
    r = Math.min(r, W / 2, H / 2);
    s.moveTo(r, 0);
    s.lineTo(W - r, 0);
    s.quadraticCurveTo(W, 0, W, r);
    s.lineTo(W, H - r);
    s.quadraticCurveTo(W, H, W - r, H);
    s.lineTo(r, H);
    s.quadraticCurveTo(0, H, 0, H - r);
    s.lineTo(0, r);
    s.quadraticCurveTo(0, 0, r, 0);
    return s;
  }

  function addHole(shape, cx, cy, r) {
    var p = new THREE.Path();
    p.absarc(cx, cy, r, 0, Math.PI * 2, true);
    shape.holes.push(p);
  }

  function buildBase(format, L) {
    var B = window.__BRAND__ || {};
    var cfg = (B.formats || {})[format] || {};
    var geo, info = {};

    if (format === "soporte") {
      var alpha = (cfg.angle || 60) * Math.PI / 180;
      var lip = cfg.lip || 2.6;
      var D = L.H * Math.cos(alpha);
      var Hb = lip + L.H * Math.sin(alpha);

      /* Perfil lateral: sx = profundidad, sy = altura. Se extruye a lo ancho. */
      var prof = new THREE.Shape();
      prof.moveTo(0, 0);
      prof.lineTo(D, 0);
      prof.lineTo(D, Hb);
      prof.lineTo(0, lip);
      prof.lineTo(0, 0);

      geo = new THREE.ExtrudeGeometry(prof, { depth: L.W, bevelEnabled: false, curveSegments: 4 });
      /* permutacion: mundoX = sz, mundoY = sx, mundoZ = sy */
      var perm = new THREE.Matrix4();
      perm.set(0, 0, 1, 0,
               1, 0, 0, 0,
               0, 1, 0, 0,
               0, 0, 0, 1);
      geo.applyMatrix4(perm);

      /* transformacion del relieve: girar alpha en X y subir hasta el labio */
      var m = new THREE.Matrix4().makeRotationX(alpha);
      m.premultiply(new THREE.Matrix4().makeTranslation(0, 0, lip));

      info = { reliefMatrix: m, depth: D, height: Hb, alpha: alpha };
      return { geometry: geo, info: info };
    }

    /* llavero y placa: placa plana con agujeros */
    var t = cfg.thickness || 3;
    var radius = format === "llavero" ? Math.min(L.W * 0.14, 7) : Math.min(L.W * 0.06, 6);
    var shape = roundedRectShape(L.W, L.H, radius);

    if (format === "llavero") {
      var rr = cfg.ringR || 2.6;
      addHole(shape, L.W / 2, L.H - (L.quiet + (L.topBand / 2)), rr);
    } else {
      var hr = cfg.holeR || 2.3;
      var hy = L.H - (L.quiet + (L.topBand / 2));
      addHole(shape, L.quiet + 3.5, hy, hr);
      addHole(shape, L.W - L.quiet - 3.5, hy, hr);
    }

    geo = new THREE.ExtrudeGeometry(shape, { depth: t, bevelEnabled: false, curveSegments: 10 });
    var m2 = new THREE.Matrix4().makeTranslation(0, 0, t);
    return { geometry: geo, info: { reliefMatrix: m2, depth: t, height: L.H, alpha: 0 } };
  }

  /* ---------------------------------------------------------------
     Mascara de la cara: el QR con estilo + el texto, rasterizados
     --------------------------------------------------------------- */
  function buildFaceMask(L, qrImage, text, pxPerMm) {
    var cols = Math.max(8, Math.round(L.W * pxPerMm));
    var rows = Math.max(8, Math.round(L.H * pxPerMm));
    var cv = document.createElement("canvas");
    cv.width = cols; cv.height = rows;
    var ctx = cv.getContext("2d", { willReadFrequently: true });
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, cols, rows);

    /* El QR: canvas con Y hacia abajo, la pieza con Y hacia arriba */
    var qx = Math.round(L.qrX * pxPerMm);
    var qs = Math.round(L.qrSize * pxPerMm);
    var qyTop = Math.round((L.H - L.qrY - L.qrSize) * pxPerMm);
    if (qrImage) {
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(qrImage, qx, qyTop, qs, qs);
    }

    /* El texto */
    if (text && L.textH > 0) {
      var fpx = Math.round(L.textH * pxPerMm);
      ctx.fillStyle = "#000";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      var family = '"Space Grotesk", "Segoe UI", Arial, sans-serif';
      ctx.font = "700 " + fpx + "px " + family;
      var maxW = Math.round(L.textW * pxPerMm);
      var w = ctx.measureText(text).width;
      if (w > maxW && w > 0) {
        fpx = Math.max(6, Math.floor(fpx * (maxW / w)));
        ctx.font = "700 " + fpx + "px " + family;
      }
      var cy = Math.round((L.H - L.textY - L.textH / 2) * pxPerMm);
      ctx.fillText(text, Math.round(cols / 2), cy);
    }

    var img = ctx.getImageData(0, 0, cols, rows).data;
    var on = new Uint8Array(cols * rows);
    for (var i = 0, p = 0; i < on.length; i++, p += 4) {
      var lum = 0.299 * img[p] + 0.587 * img[p + 1] + 0.114 * img[p + 2];
      on[i] = (img[p + 3] > 40 && lum < 128) ? 1 : 0;
    }
    return { on: on, cols: cols, rows: rows };
  }

  /* ---------------------------------------------------------------
     Construccion del modelo completo
     --------------------------------------------------------------- */
  function buildModel(opts) {
    return loadEngine().then(function () {
      var format = opts.format;
      var W = opts.sizeMm;
      var relief = opts.reliefMm;
      var n = opts.moduleCount;
      var text = (opts.text || "").trim();

      var L = layout(format, W, n, !!text);

      /* Resolucion: ~10 celdas por modulo, con techo para no explotar */
      var pxPerMm = 10 / L.moduleMm;
      var maxSide = 1100;
      var side = Math.max(L.W, L.H) * pxPerMm;
      if (side > maxSide) pxPerMm = pxPerMm * (maxSide / side);

      var mask = buildFaceMask(L, opts.qrImage, text, pxPerMm);
      var cell = 1 / pxPerMm;
      var cols = mask.cols, rows = mask.rows, on = mask.on;
      var rects = gridRects(function (r, c) { return on[r * cols + c] === 1; }, cols, rows);

      /* Relieve: una caja por rectangulo, hundida 0,15 mm en la base */
      var sink = 0.15;
      var eps = 0.01;
      var arr = [];
      for (var i = 0; i < rects.length; i++) {
        var q = rects[i];
        var x = q.c * cell - eps;
        var y = (rows - q.r - q.h) * cell - eps;   /* voltear el eje Y */
        pushBox(arr, x, y, -sink, q.w * cell + 2 * eps, q.h * cell + 2 * eps, relief + sink);
      }
      var reliefPos = new Float32Array(arr);
      arr = null;

      var base = buildBase(format, L);

      /* Aplicar la transformacion de la cara al relieve */
      var rg = new THREE.BufferGeometry();
      rg.setAttribute("position", new THREE.BufferAttribute(reliefPos, 3));
      rg.applyMatrix4(base.info.reliefMatrix);

      var bg = base.geometry.index ? base.geometry.toNonIndexed() : base.geometry;

      var basePos = bg.getAttribute("position").array;
      var relPos = rg.getAttribute("position").array;

      /* Todo al octante positivo (los slicers colocan desde el origen) */
      var min = [Infinity, Infinity, Infinity];
      var max = [-Infinity, -Infinity, -Infinity];
      function scan(p) {
        for (var i = 0; i < p.length; i += 3) {
          for (var k = 0; k < 3; k++) {
            var v = p[i + k];
            if (v < min[k]) min[k] = v;
            if (v > max[k]) max[k] = v;
          }
        }
      }
      scan(basePos); scan(relPos);
      function shift(p) {
        var q = new Float32Array(p.length);
        for (var i = 0; i < p.length; i += 3) {
          q[i] = p[i] - min[0]; q[i + 1] = p[i + 1] - min[1]; q[i + 2] = p[i + 2] - min[2];
        }
        return q;
      }
      var outBase = shift(basePos), outRelief = shift(relPos);

      return {
        format: format,
        base: outBase,
        relief: outRelief,
        layout: L,
        info: {
          moduleMm: L.moduleMm,
          moduleCount: n,
          rects: rects.length,
          triangles: (outBase.length + outRelief.length) / 9,
          sizeX: max[0] - min[0],
          sizeY: max[1] - min[1],
          sizeZ: max[2] - min[2],
          reliefMm: relief,
          text: text
        }
      };
    });
  }

  /* ---------------------------------------------------------------
     Soldadura de vertices (menos peso, malla mas limpia)
     --------------------------------------------------------------- */
  function weld(pos) {
    var map = new Map();
    var verts = [];
    var tris = [];
    var idx = new Int32Array(pos.length / 3);
    for (var i = 0, v = 0; i < pos.length; i += 3, v++) {
      var x = Math.round(pos[i] * 1000) / 1000;
      var y = Math.round(pos[i + 1] * 1000) / 1000;
      var z = Math.round(pos[i + 2] * 1000) / 1000;
      var key = x + "|" + y + "|" + z;
      var id = map.get(key);
      if (id === undefined) {
        id = verts.length / 3;
        map.set(key, id);
        verts.push(x, y, z);
      }
      idx[v] = id;
    }
    for (var t = 0; t < idx.length; t += 3) {
      var a = idx[t], b = idx[t + 1], c = idx[t + 2];
      if (a === b || b === c || a === c) continue;   /* triangulo degenerado */
      tris.push(a, b, c);
    }
    return { verts: verts, tris: tris };
  }

  function num(v) { return String(Math.round(v * 1000) / 1000); }

  function meshXML(pos) {
    var w = weld(pos);
    var out = ["<mesh><vertices>"];
    for (var i = 0; i < w.verts.length; i += 3) {
      out.push('<vertex x="' + num(w.verts[i]) + '" y="' + num(w.verts[i + 1]) + '" z="' + num(w.verts[i + 2]) + '"/>');
    }
    out.push("</vertices><triangles>");
    for (var t = 0; t < w.tris.length; t += 3) {
      out.push('<triangle v1="' + w.tris[t] + '" v2="' + w.tris[t + 1] + '" v3="' + w.tris[t + 2] + '"/>');
    }
    out.push("</triangles></mesh>");
    return { xml: out.join(""), triangles: w.tris.length / 3, vertices: w.verts.length / 3 };
  }

  function hex8(c) {
    var h = String(c || "#000000").replace("#", "").trim();
    if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
    if (h.length !== 6) h = "000000";
    return "#" + h.toUpperCase() + "FF";        /* el byte alfa NO es opcional */
  }

  /* ---------------------------------------------------------------
     Exportar 3MF: un zip con XML dentro, los colores incluidos
     --------------------------------------------------------------- */
  function export3MF(model, colors) {
    if (!window.JSZip) return Promise.reject(new Error("JSZip no disponible"));
    var mBase = meshXML(model.base);
    var mRel = meshXML(model.relief);

    var xml = '<?xml version="1.0" encoding="UTF-8"?>\n' +
      '<model unit="millimeter" xml:lang="es-ES" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n' +
      '<metadata name="Application">QR3D</metadata>\n' +
      '<metadata name="Title">' + "Codigo QR 3D" + '</metadata>\n' +
      '<resources>\n' +
      '<basematerials id="1">' +
      '<base name="Base" displaycolor="' + hex8(colors.base) + '"/>' +
      '<base name="Codigo" displaycolor="' + hex8(colors.relief) + '"/>' +
      '</basematerials>\n' +
      '<object id="2" type="model" pid="1" pindex="0" name="Base">' + mBase.xml + '</object>\n' +
      '<object id="3" type="model" pid="1" pindex="1" name="Codigo QR">' + mRel.xml + '</object>\n' +
      '</resources>\n' +
      '<build><item objectid="2"/><item objectid="3"/></build>\n' +
      '</model>\n';

    var contentTypes = '<?xml version="1.0" encoding="UTF-8"?>' +
      '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">' +
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>' +
      '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>' +
      '</Types>';

    var rels = '<?xml version="1.0" encoding="UTF-8"?>' +
      '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
      '<Relationship Id="rel0" Target="/3D/3dmodel.model" ' +
      'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>' +
      '</Relationships>';

    var zip = new window.JSZip();
    zip.file("[Content_Types].xml", contentTypes);
    zip.folder("_rels").file(".rels", rels);
    zip.folder("3D").file("3dmodel.model", xml);

    return zip.generateAsync({ type: "blob", mimeType: "model/3mf", compression: "DEFLATE" })
      .then(function (blob) {
        return { blob: blob, triangles: mBase.triangles + mRel.triangles };
      });
  }

  /* ---------------------------------------------------------------
     Exportar STL binario (dos piezas en un zip) para impresoras antiguas
     --------------------------------------------------------------- */
  function stlBinary(pos, name) {
    var tri = pos.length / 9;
    var buf = new ArrayBuffer(84 + tri * 50);
    var dv = new DataView(buf);
    var enc = "QR3D " + name;
    for (var i = 0; i < 80; i++) dv.setUint8(i, i < enc.length ? enc.charCodeAt(i) : 32);
    dv.setUint32(80, tri, true);
    var o = 84;
    for (var t = 0; t < tri; t++) {
      var p = t * 9;
      var ax = pos[p], ay = pos[p + 1], az = pos[p + 2];
      var bx = pos[p + 3], by = pos[p + 4], bz = pos[p + 5];
      var cx = pos[p + 6], cy = pos[p + 7], cz = pos[p + 8];
      var ux = bx - ax, uy = by - ay, uz = bz - az;
      var vx = cx - ax, vy = cy - ay, vz = cz - az;
      var nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
      var len = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
      dv.setFloat32(o, nx / len, true); dv.setFloat32(o + 4, ny / len, true); dv.setFloat32(o + 8, nz / len, true);
      dv.setFloat32(o + 12, ax, true); dv.setFloat32(o + 16, ay, true); dv.setFloat32(o + 20, az, true);
      dv.setFloat32(o + 24, bx, true); dv.setFloat32(o + 28, by, true); dv.setFloat32(o + 32, bz, true);
      dv.setFloat32(o + 36, cx, true); dv.setFloat32(o + 40, cy, true); dv.setFloat32(o + 44, cz, true);
      dv.setUint16(o + 48, 0, true);
      o += 50;
    }
    return buf;
  }

  function exportSTLZip(model, slug) {
    if (!window.JSZip) return Promise.reject(new Error("JSZip no disponible"));
    var zip = new window.JSZip();
    zip.file(slug + "-1-base.stl", stlBinary(model.base, "base"));
    zip.file(slug + "-2-codigo.stl", stlBinary(model.relief, "codigo"));
    zip.file("LEEME.txt",
      "QR3D - dos piezas en STL\r\n" +
      "========================\r\n\r\n" +
      "1. Importa los DOS archivos en el programa de tu impresora.\r\n" +
      "2. Coloca ambos en la posicion 0, 0 (sin mover nada): ya encajan.\r\n" +
      "3. Asigna un filamento a cada pieza:\r\n" +
      "     -1-base.stl    -> color claro (la base)\r\n" +
      "     -2-codigo.stl  -> color oscuro (el codigo y el texto en relieve)\r\n\r\n" +
      "Si tu impresora es de un solo color, programa un cambio de filamento\r\n" +
      "a la altura en la que empieza el relieve.\r\n\r\n" +
      "El STL no guarda colores. Si tu programa admite 3MF, usa mejor el 3MF.\r\n");
    return zip.generateAsync({ type: "blob", compression: "DEFLATE" });
  }

  /* ---------------------------------------------------------------
     Vista previa 3D
     --------------------------------------------------------------- */
  var viewer = {
    el: null, renderer: null, scene: null, camera: null, controls: null,
    group: null, meshBase: null, meshRelief: null,
    visible: false, running: false, ready: false, failed: false,
    lastFormat: null
  };

  function initViewer(el) {
    viewer.el = el;
    var w = el.clientWidth || 400;
    var h = el.clientHeight || 340;

    viewer.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    viewer.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    viewer.renderer.setSize(w, h, false);
    viewer.renderer.domElement.style.width = "100%";
    viewer.renderer.domElement.style.height = "100%";
    el.insertBefore(viewer.renderer.domElement, el.firstChild);

    viewer.scene = new THREE.Scene();
    viewer.camera = new THREE.PerspectiveCamera(32, w / h, 0.5, 4000);
    viewer.camera.position.set(0, 40, 160);

    viewer.scene.add(new THREE.HemisphereLight(0xffffff, 0xa8b2c4, 2.0));
    var d1 = new THREE.DirectionalLight(0xffffff, 2.4); d1.position.set(60, 90, 120);
    var d2 = new THREE.DirectionalLight(0xffffff, 0.9); d2.position.set(-80, 30, -60);
    viewer.scene.add(d1, d2);

    viewer.controls = new OrbitControls(viewer.camera, viewer.renderer.domElement);
    viewer.controls.enableDamping = true;
    viewer.controls.dampingFactor = 0.09;
    viewer.controls.enablePan = false;
    viewer.controls.minDistance = 30;
    viewer.controls.maxDistance = 900;

    viewer.group = new THREE.Group();
    viewer.scene.add(viewer.group);

    if (window.ResizeObserver) {
      var ro = new ResizeObserver(function () { resize(); });
      ro.observe(el);
    } else {
      window.addEventListener("resize", resize);
    }
    viewer.ready = true;
    loop();
  }

  function resize() {
    if (!viewer.renderer || !viewer.el) return;
    var w = viewer.el.clientWidth, h = viewer.el.clientHeight;
    if (!w || !h) return;
    viewer.renderer.setSize(w, h, false);
    viewer.camera.aspect = w / h;
    viewer.camera.updateProjectionMatrix();
  }

  function loop() {
    if (viewer.running) return;
    viewer.running = true;
    function frame() {
      requestAnimationFrame(frame);
      if (!viewer.visible || document.hidden || !viewer.renderer) return;
      if (viewer.controls) viewer.controls.update();
      viewer.renderer.render(viewer.scene, viewer.camera);
    }
    frame();
  }

  function disposeMesh(m) {
    if (!m) return;
    viewer.group.remove(m);
    if (m.geometry) m.geometry.dispose();
    if (m.material) m.material.dispose();
  }

  function setModel(model, colors) {
    if (!viewer.ready) return;
    disposeMesh(viewer.meshBase); disposeMesh(viewer.meshRelief);

    function mk(pos, color) {
      var g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.BufferAttribute(pos.slice(0), 3));
      g.computeVertexNormals();
      var mat = new THREE.MeshStandardMaterial({
        color: new THREE.Color(color), roughness: 0.72, metalness: 0.02
      });
      return new THREE.Mesh(g, mat);
    }
    viewer.meshBase = mk(model.base, colors.base);
    viewer.meshRelief = mk(model.relief, colors.relief);
    viewer.group.add(viewer.meshBase, viewer.meshRelief);

    /* La pieza se construye con Z hacia arriba; three trabaja con Y hacia arriba */
    viewer.group.rotation.set(model.format === "soporte" ? -Math.PI / 2 : 0, 0, 0);

    var box = new THREE.Box3().setFromObject(viewer.group);
    var c = box.getCenter(new THREE.Vector3());
    viewer.group.position.set(-c.x + viewer.group.position.x,
                              -c.y + viewer.group.position.y,
                              -c.z + viewer.group.position.z);

    if (viewer.lastFormat !== model.format) {
      viewer.lastFormat = model.format;
      fitCamera(model.format);
    }
  }

  function fitCamera(format) {
    var box = new THREE.Box3().setFromObject(viewer.group);
    var size = box.getSize(new THREE.Vector3());
    var radius = Math.max(size.x, size.y, size.z) * 0.62;
    var fov = viewer.camera.fov * Math.PI / 180;
    var dist = (radius / Math.sin(fov / 2)) * 1.28;
    var dir = format === "soporte"
      ? new THREE.Vector3(0.46, 0.40, 1).normalize()
      : new THREE.Vector3(0.10, 0.12, 1).normalize();
    viewer.camera.position.copy(dir.multiplyScalar(dist));
    viewer.camera.lookAt(0, 0, 0);
    viewer.controls.target.set(0, 0, 0);
    viewer.controls.update();
  }

  function setColors(colors) {
    if (viewer.meshBase) viewer.meshBase.material.color.set(colors.base);
    if (viewer.meshRelief) viewer.meshRelief.material.color.set(colors.relief);
  }

  function activate(el, onReady, onFail) {
    if (viewer.ready) { onReady && onReady(); return; }
    if (viewer.failed) { onFail && onFail("nowebgl"); return; }
    if (!hasWebGL()) {
      viewer.failed = true;
      onFail && onFail("nowebgl");
      return;
    }
    loadEngine().then(function () {
      initViewer(el);
      viewer.visible = true;
      onReady && onReady();
    }).catch(function (e) {
      viewer.failed = true;
      console.warn("[qr3d] motor 3D no disponible:", e);
      onFail && onFail("engine");
    });
  }

  window.__QR3D__ = {
    loadEngine: loadEngine,
    hasWebGL: hasWebGL,
    layout: layout,
    buildModel: buildModel,
    export3MF: export3MF,
    exportSTLZip: exportSTLZip,
    activate: activate,
    setModel: setModel,
    setColors: setColors,
    resize: resize,
    setVisible: function (v) { viewer.visible = !!v; if (v) resize(); },
    isReady: function () { return viewer.ready; },
    hasFailed: function () { return viewer.failed; }
  };
})();
