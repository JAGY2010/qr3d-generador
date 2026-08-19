/* =============================================================
   main.js - QR3D
   Disenador del codigo QR (imagen) + puente con el motor 3D (qr3d.js)
   + huecos de publicidad. Patron IIFE, sin dependencias de build.
   ============================================================= */
(function () {
  "use strict";

  var B = window.__BRAND__ || {};
  var QR3D = window.__QR3D__ || null;

  /* ---------------- helpers ---------------- */
  var $ = function (s, sc) { return (sc || document).querySelector(s); };
  var $$ = function (s, sc) { return Array.prototype.slice.call((sc || document).querySelectorAll(s)); };
  function safe(fn, name) { try { return fn(); } catch (e) { console.warn("[" + name + "]", e); } }
  function debounce(fn, ms) {
    var t = null;
    return function () {
      var a = arguments, self = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(self, a); }, ms);
    };
  }
  function fmt(n, d) {
    var v = Number(n);
    if (!isFinite(v)) return "-";
    return v.toFixed(d === undefined ? 1 : d).replace(".", ",");
  }

  /* ---------------- estado ---------------- */
  var state = {
    mode: "link",
    data: "https://ejemplo.com/carta",
    ssid: "", pass: "", enc: "WPA",
    style: "clasico",
    fg: "#141821",
    bg: "#f4f2ec",
    center: null,          /* { kind, src, sil } */
    format: "soporte",
    size: 78,
    text: "",
    relief: 1.2,
    moduleCount: 0,
    model: null,
    enabled3D: false,
    building: false
  };

  var qrInstance = null;
  var gen3d = 0;

  /* ---------------- contenido del codigo ---------------- */
  function escWifi(s) {
    return String(s == null ? "" : s).replace(/([\\;,:"])/g, "\\$1");
  }
  function payload() {
    if (state.mode === "wifi") {
      var t = state.enc === "nopass" ? "nopass" : state.enc;
      var p = state.enc === "nopass" ? "" : escWifi(state.pass);
      return "WIFI:T:" + t + ";S:" + escWifi(state.ssid || "MiWifi") + ";P:" + p + ";;";
    }
    var d = (state.data || "").trim();
    if (!d) return "https://ejemplo.com";
    /* dominio suelto -> https:// */
    if (!/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(d) && /^[\w-]+(\.[\w-]+)+([/?#].*)?$/.test(d)) {
      d = "https://" + d;
    }
    return d;
  }
  function slug() {
    var p = payload();
    if (state.mode === "wifi") return "qr-wifi-" + (state.ssid || "red").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 24);
    var host = "";
    try { host = new URL(p).hostname.replace(/^www\./, ""); } catch (e) { host = ""; }
    var s = (host || p).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 32);
    return "qr-" + (s || "codigo");
  }

  /* ---------------- opciones del codigo ---------------- */
  function styleDef() { return (B.styles || {})[state.style] || { dots: "square", corners: "square", cornerDot: "square" }; }

  function qrOptions(size, type, mono) {
    var st = styleDef();
    var fg = mono ? "#000000" : state.fg;
    var bg = mono ? "#ffffff" : state.bg;
    var img = mono ? (state.center && state.center.sil) : (state.center && state.center.src);
    var o = {
      width: size, height: size, type: type || "canvas",
      data: payload(),
      margin: mono ? 0 : Math.round(size * 0.045),
      qrOptions: { errorCorrectionLevel: state.center ? "H" : "M" },
      imageOptions: { hideBackgroundDots: true, imageSize: 0.34, margin: Math.round(size * (mono ? 0.006 : 0.012)), crossOrigin: "anonymous" },
      dotsOptions: { color: fg, type: st.dots },
      backgroundOptions: { color: bg },
      cornersSquareOptions: { color: fg, type: st.corners },
      cornersDotOptions: { color: fg, type: st.cornerDot }
    };
    if (img) o.image = img;
    return o;
  }

  /* ---------------- vista previa 2D ---------------- */
  function renderQR() {
    if (!window.QRCodeStyling) return;
    var stage = $("#qr-stage");
    if (!stage) return;
    var size = 320;
    var opts = qrOptions(size, "canvas", false);

    if (!qrInstance) {
      var ph = $("#qr-placeholder");
      if (ph) ph.remove();
      qrInstance = new window.QRCodeStyling(opts);
      qrInstance.append(stage);
    } else {
      qrInstance.update(opts);
    }
    readModuleCount(0);
  }

  function readModuleCount(tries) {
    var n = 0;
    try { n = qrInstance && qrInstance._qr ? qrInstance._qr.getModuleCount() : 0; } catch (e) { n = 0; }
    if (!n && tries < 6) { setTimeout(function () { readModuleCount(tries + 1); }, 60); return; }
    if (n && n !== state.moduleCount) {
      state.moduleCount = n;
      var lbl = $("#qr-modules");
      if (lbl) lbl.textContent = n + " x " + n + " modulos";
      updateSpecs();
      scheduleBuild3D();
    } else if (n) {
      var lbl2 = $("#qr-modules");
      if (lbl2) lbl2.textContent = n + " x " + n + " modulos";
    }
  }

  /* ---------------- mascara en blanco y negro para el relieve ---------------- */
  function maskImage(n) {
    var px = Math.max(120, n * 10);
    var inst = new window.QRCodeStyling(qrOptions(px, "canvas", true));
    return inst.getRawData("png").then(function (blob) {
      if (window.createImageBitmap) return createImageBitmap(blob);
      return new Promise(function (res, rej) {
        var url = URL.createObjectURL(blob);
        var im = new Image();
        im.onload = function () { URL.revokeObjectURL(url); res(im); };
        im.onerror = function (e) { URL.revokeObjectURL(url); rej(e); };
        im.src = url;
      });
    });
  }

  /* ---------------- silueta del logo / emoji ---------------- */
  function loadImg(src) {
    return new Promise(function (res, rej) {
      var im = new Image();
      im.crossOrigin = "anonymous";
      im.onload = function () { res(im); };
      im.onerror = rej;
      im.src = src;
    });
  }

  function silhouette(src) {
    return loadImg(src).then(function (im) {
      var S = 320;
      var cv = document.createElement("canvas");
      cv.width = S; cv.height = S;
      var ctx = cv.getContext("2d", { willReadFrequently: true });
      var w = im.width || S, h = im.height || S;
      var k = Math.min(S / w, S / h);
      var dw = w * k, dh = h * k;
      ctx.drawImage(im, (S - dw) / 2, (S - dh) / 2, dw, dh);

      var d = ctx.getImageData(0, 0, S, S);
      var p = d.data, transparent = 0, total = S * S;
      for (var i = 3; i < p.length; i += 4) if (p[i] < 40) transparent++;
      var useAlpha = (transparent / total) > 0.04;

      for (var j = 0; j < p.length; j += 4) {
        var on;
        if (useAlpha) {
          on = p[j + 3] > 120;
        } else {
          var lum = 0.299 * p[j] + 0.587 * p[j + 1] + 0.114 * p[j + 2];
          on = p[j + 3] > 60 && lum < 145;
        }
        if (on) { p[j] = 0; p[j + 1] = 0; p[j + 2] = 0; p[j + 3] = 255; }
        else { p[j + 3] = 0; }
      }
      ctx.putImageData(d, 0, 0);
      return cv.toDataURL("image/png");
    });
  }

  function emojiDataURL(emoji) {
    var S = 256;
    var cv = document.createElement("canvas");
    cv.width = S; cv.height = S;
    var ctx = cv.getContext("2d");
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = Math.round(S * 0.78) + 'px "Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif';
    ctx.fillText(emoji, S / 2, S / 2 + S * 0.04);
    return cv.toDataURL("image/png");
  }

  function setCenter(kind, src) {
    if (!src) {
      state.center = null;
      $("#btn-clear-center").hidden = true;
      $$("#emoji-grid button").forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
      onChange();
      return;
    }
    silhouette(src).then(function (sil) {
      state.center = { kind: kind, src: src, sil: sil };
      $("#btn-clear-center").hidden = false;
      onChange();
    }).catch(function (e) {
      console.warn("[silueta]", e);
      state.center = { kind: kind, src: src, sil: src };
      $("#btn-clear-center").hidden = false;
      onChange();
    });
  }

  /* ---------------- contraste y avisos de impresion ---------------- */
  function toRGB(hex) {
    var h = String(hex).replace("#", "");
    if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
  }
  function relLum(hex) {
    var c = toRGB(hex).map(function (v) {
      v /= 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  }
  function contrast(a, b) {
    var l1 = relLum(a), l2 = relLum(b);
    var hi = Math.max(l1, l2), lo = Math.min(l1, l2);
    return (hi + 0.05) / (lo + 0.05);
  }

  var ICO_OK = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>';
  var ICO_WARN = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>';

  function note(kind, html) {
    return '<div class="note note--' + kind + '">' + (kind === "ok" ? ICO_OK : ICO_WARN) + "<span>" + html + "</span></div>";
  }

  function currentLayout() {
    if (!QR3D || !state.moduleCount) return null;
    return QR3D.layout(state.format, state.size, state.moduleCount, !!state.text.trim());
  }

  function updateSpecs() {
    var L = currentLayout();
    var specs = $("#specs"), checks = $("#checks"), objSize = $("#obj-size");
    if (!specs || !checks) return;

    if (!L) { specs.innerHTML = ""; checks.innerHTML = ""; return; }

    var mod = L.moduleMm;
    var depth = "";
    var cfg = (B.formats || {})[state.format] || {};
    if (state.format === "soporte") {
      var a = (cfg.angle || 60) * Math.PI / 180;
      depth = fmt(L.H * Math.cos(a), 0) + " mm de fondo";
    } else {
      depth = fmt(cfg.thickness || 3, 1) + " mm de grosor";
    }

    if (objSize) objSize.textContent = fmt(L.W, 0) + " x " + fmt(L.H, 0) + " mm";

    var tri = state.model ? state.model.info.triangles : 0;
    specs.innerHTML =
      "<span>Pieza <b>" + fmt(L.W, 0) + " x " + fmt(L.H, 0) + " mm</b></span>" +
      "<span>" + depth + "</span>" +
      "<span>Cada cuadrito <b>" + fmt(mod, 2) + " mm</b></span>" +
      "<span>Relieve <b>" + fmt(state.relief, 1) + " mm</b></span>" +
      (tri ? "<span><b>" + tri.toLocaleString("es-ES") + "</b> triangulos</span>" : "");

    var out = [];
    var ratio = contrast(state.fg, state.bg);
    var minC = (B.print && B.print.minContrast) || 3;
    var minM = (B.print && B.print.minModuleMm) || 1.5;

    if (ratio < minC) {
      out.push(note("bad", "<b>No se va a escanear:</b> el contraste entre los dos colores es de " + fmt(ratio, 1) + ":1. Elige una base clara y un codigo oscuro."));
    } else if (relLum(state.fg) > relLum(state.bg)) {
      out.push(note("warn", "<b>Codigo mas claro que la base:</b> la mayoria de moviles lo leen igual, pero algunos antiguos no. Lo seguro es al reves."));
    } else {
      out.push(note("ok", "Contraste " + fmt(ratio, 1) + ":1. Se leera bien impreso."));
    }

    if (mod < minM) {
      out.push(note("bad", "<b>Cuadritos demasiado pequenos</b> (" + fmt(mod, 2) + " mm). Por debajo de 1,5 mm la boquilla los emborrona: agranda la pieza o acorta el enlace."));
    } else if (mod < minM + 0.3) {
      out.push(note("warn", "Cuadritos justos (" + fmt(mod, 2) + " mm). Funciona, pero con 0,2 mm de capa y una boquilla de 0,4 mm ve al limite."));
    } else {
      out.push(note("ok", "Cada cuadrito mide " + fmt(mod, 2) + " mm: tamano de sobra para imprimir."));
    }

    if (state.center) {
      out.push(note("warn", "Con logo o emoji en el centro se tapan modulos. Ya subimos la correccion de errores al maximo, pero prueba a escanear una unidad antes de imprimir muchas."));
    }

    checks.innerHTML = out.join("");
  }

  /* ---------------- construccion del modelo 3D ---------------- */
  function viewerMsg(text, spinner) {
    var box = $("#viewer-msg"), t = $("#viewer-msg-text");
    if (!box || !t) return;
    if (text === null) { box.hidden = true; return; }
    box.hidden = false;
    t.textContent = text;
    var sp = box.querySelector(".spinner");
    if (sp) sp.style.display = spinner === false ? "none" : "";
  }

  function build3D() {
    if (!QR3D || !state.enabled3D || !state.moduleCount || !window.QRCodeStyling) return Promise.resolve(null);
    var my = ++gen3d;
    state.building = true;
    return maskImage(state.moduleCount).then(function (img) {
      if (my !== gen3d) return null;
      return QR3D.buildModel({
        format: state.format,
        sizeMm: state.size,
        reliefMm: state.relief,
        moduleCount: state.moduleCount,
        qrImage: img,
        text: state.text
      });
    }).then(function (model) {
      if (!model || my !== gen3d) return null;
      state.model = model;
      state.building = false;
      if (QR3D.isReady()) {
        QR3D.setModel(model, { base: state.bg, relief: state.fg });
        viewerMsg(null);
      }
      updateSpecs();
      return model;
    }).catch(function (e) {
      state.building = false;
      console.warn("[build3D]", e);
      if (!QR3D.isReady()) viewerMsg("No se ha podido preparar la vista 3D en este navegador. Las descargas de imagen siguen funcionando.", false);
      return null;
    });
  }

  var scheduleBuild3D = debounce(function () { build3D(); }, 320);

  /* ---------------- activacion perezosa del visor ---------------- */
  function enable3D() {
    if (state.enabled3D) return;
    state.enabled3D = true;
    var el = $("#viewer");
    if (!el || !QR3D) return;
    viewerMsg("Preparando la vista 3D...");
    QR3D.activate(el, function () {
      QR3D.setVisible(true);
      if (state.model) { QR3D.setModel(state.model, { base: state.bg, relief: state.fg }); viewerMsg(null); }
      build3D();
    }, function (why) {
      viewerMsg(why === "nowebgl"
        ? "Tu navegador no tiene aceleracion 3D activada, asi que no podemos mostrar la vista previa. Las descargas siguen funcionando igual."
        : "No se ha podido cargar el motor 3D. Las descargas de imagen siguen funcionando.", false);
      build3D();
    });
  }

  function initLazy3D() {
    var el = $("#viewer");
    if (!el) return;

    function check() {
      /* Pestana en segundo plano: sin tamano, el observer puede no disparar nunca */
      if (!window.innerHeight) { setTimeout(check, 700); return; }
      var r = el.getBoundingClientRect();
      if (r.top < window.innerHeight + 200 && r.bottom > -200) enable3D();
    }

    if (window.IntersectionObserver) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { enable3D(); QR3D && QR3D.setVisible(true); }
          else if (QR3D && QR3D.isReady()) QR3D.setVisible(false);
        });
      }, { rootMargin: "200px", threshold: 0.01 });
      io.observe(el);
    }
    setTimeout(check, 400);
    document.addEventListener("visibilitychange", function () {
      if (!document.hidden) { check(); if (QR3D && QR3D.isReady()) QR3D.resize(); }
    });
  }

  /* ---------------- descargas ---------------- */
  function saveBlob(blob, name) {
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url; a.download = name;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { document.body.removeChild(a); URL.revokeObjectURL(url); }, 4000);
    document.dispatchEvent(new CustomEvent("qr3d:downloaded", { detail: { name: name } }));
  }

  function busy(btn, on, label) {
    if (!btn) return;
    btn.disabled = !!on;
    if (label !== undefined) {
      var span = btn.querySelector("span");
      if (span) span.textContent = label;
      else btn.textContent = label;
    }
  }

  function downloadImage(ext) {
    if (!window.QRCodeStyling) return;
    var size = ext === "png" ? 1200 : 1000;
    var inst = new window.QRCodeStyling(qrOptions(size, ext === "svg" ? "svg" : "canvas", false));
    inst.getRawData(ext).then(function (blob) {
      saveBlob(blob, slug() + "." + ext);
    }).catch(function (e) { console.warn("[descarga " + ext + "]", e); });
  }

  function ensureModel() {
    if (state.model && !state.building) return Promise.resolve(state.model);
    state.enabled3D = true;
    return build3D();
  }

  function download3MF() {
    var btn = $("#btn-3mf"), label = $("#btn-3mf-label");
    var prev = label ? label.textContent : "";
    if (label) label.textContent = "Preparando el archivo...";
    if (btn) btn.disabled = true;
    ensureModel().then(function (model) {
      if (!model) throw new Error("sin modelo");
      return QR3D.export3MF(model, { base: state.bg, relief: state.fg });
    }).then(function (res) {
      saveBlob(res.blob, slug() + "-" + state.format + ".3mf");
    }).catch(function (e) {
      console.warn("[3mf]", e);
      alert("No se ha podido generar el archivo 3D. Prueba a recargar la pagina.");
    }).then(function () {
      if (label) label.textContent = prev;
      if (btn) btn.disabled = false;
    });
  }

  function downloadSTL() {
    var btn = $("#btn-stl");
    var prev = btn ? btn.textContent : "";
    if (btn) { btn.disabled = true; btn.textContent = "Preparando los STL..."; }
    ensureModel().then(function (model) {
      if (!model) throw new Error("sin modelo");
      return QR3D.exportSTLZip(model, slug() + "-" + state.format);
    }).then(function (blob) {
      saveBlob(blob, slug() + "-" + state.format + "-stl.zip");
    }).catch(function (e) {
      console.warn("[stl]", e);
      alert("No se han podido generar los STL. Prueba a recargar la pagina.");
    }).then(function () {
      if (btn) { btn.disabled = false; btn.textContent = prev; }
    });
  }

  /* ---------------- cambios ---------------- */
  var renderSoon = debounce(function () { renderQR(); }, 130);

  function onChange(heavy) {
    renderSoon();
    updateSpecs();
    if (heavy !== false) scheduleBuild3D();
  }

  /* ---------------- montajes de UI ---------------- */
  function mountPalettes() {
    var box = $("#palettes");
    if (!box || box.children.length) return;
    (B.palettes || []).forEach(function (p) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "swatch";
      b.title = p[0] + " sobre " + p[1];
      b.setAttribute("aria-label", "Usar codigo " + p[0] + " sobre fondo " + p[1]);
      b.innerHTML = '<i style="background:' + p[0] + '"></i><i style="background:' + p[1] + '"></i>';
      b.addEventListener("click", function () {
        state.fg = p[0]; state.bg = p[1];
        syncColorInputs();
        if (QR3D && QR3D.isReady()) QR3D.setColors({ base: state.bg, relief: state.fg });
        onChange(false);
      });
      box.appendChild(b);
    });
  }

  function mountEmojis() {
    var box = $("#emoji-grid");
    if (!box || box.children.length) return;
    (B.emojis || []).forEach(function (e) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = e;
      b.setAttribute("aria-pressed", "false");
      b.setAttribute("aria-label", "Poner " + e + " en el centro");
      b.addEventListener("click", function () {
        var already = b.getAttribute("aria-pressed") === "true";
        $$("#emoji-grid button").forEach(function (o) { o.setAttribute("aria-pressed", "false"); });
        if (already) { setCenter(null, null); return; }
        b.setAttribute("aria-pressed", "true");
        setCenter("emoji", emojiDataURL(e));
      });
      box.appendChild(b);
    });
  }

  function syncColorInputs() {
    $("#in-fg").value = state.fg;
    $("#in-bg").value = state.bg;
    $("#in-fg-hex").value = state.fg.toUpperCase();
    $("#in-bg-hex").value = state.bg.toUpperCase();
  }

  function initControls() {
    /* modo de contenido */
    $$("[role=tab]").forEach(function (t) {
      t.addEventListener("click", function () {
        $$("[role=tab]").forEach(function (o) { o.setAttribute("aria-selected", "false"); });
        t.setAttribute("aria-selected", "true");
        state.mode = t.getAttribute("data-mode");
        $("#pane-link").hidden = state.mode !== "link";
        $("#pane-wifi").hidden = state.mode !== "wifi";
        onChange();
      });
    });

    $("#in-data").addEventListener("input", function () { state.data = this.value; onChange(); });
    $("#in-ssid").addEventListener("input", function () { state.ssid = this.value; onChange(); });
    $("#in-pass").addEventListener("input", function () { state.pass = this.value; onChange(); });
    $("#in-enc").addEventListener("change", function () { state.enc = this.value; onChange(); });

    /* estilo */
    $$("#style-chips .chip").forEach(function (c) {
      c.addEventListener("click", function () {
        $$("#style-chips .chip").forEach(function (o) { o.setAttribute("aria-pressed", "false"); });
        c.setAttribute("aria-pressed", "true");
        state.style = c.getAttribute("data-style");
        onChange();
      });
    });

    /* colores */
    function applyColor(which, value) {
      if (!/^#[0-9a-fA-F]{6}$/.test(value)) return;
      state[which] = value.toLowerCase();
      syncColorInputs();
      if (QR3D && QR3D.isReady()) QR3D.setColors({ base: state.bg, relief: state.fg });
      onChange(false);
    }
    $("#in-fg").addEventListener("input", function () { applyColor("fg", this.value); });
    $("#in-bg").addEventListener("input", function () { applyColor("bg", this.value); });
    $("#in-fg-hex").addEventListener("change", function () { applyColor("fg", this.value.trim()); });
    $("#in-bg-hex").addEventListener("change", function () { applyColor("bg", this.value.trim()); });
    $("#btn-swap").addEventListener("click", function () {
      var a = state.fg; state.fg = state.bg; state.bg = a;
      syncColorInputs();
      if (QR3D && QR3D.isReady()) QR3D.setColors({ base: state.bg, relief: state.fg });
      onChange(false);
    });

    /* logo */
    $("#in-logo").addEventListener("change", function () {
      var f = this.files && this.files[0];
      if (!f) return;
      var rd = new FileReader();
      rd.onload = function () {
        $$("#emoji-grid button").forEach(function (o) { o.setAttribute("aria-pressed", "false"); });
        setCenter("logo", rd.result);
      };
      rd.readAsDataURL(f);
      this.value = "";
    });
    $("#btn-clear-center").addEventListener("click", function () { setCenter(null, null); });

    /* formato */
    $$("#format-chips .chip").forEach(function (c) {
      c.addEventListener("click", function () {
        $$("#format-chips .chip").forEach(function (o) { o.setAttribute("aria-pressed", "false"); });
        c.setAttribute("aria-pressed", "true");
        state.format = c.getAttribute("data-format");
        var cfg = (B.formats || {})[state.format] || {};
        var sl = $("#in-size");
        sl.min = cfg.min || 40; sl.max = cfg.max || 140;
        state.size = cfg.defaultSize || 78;
        sl.value = state.size;
        $("#size-value").textContent = state.size + " mm";
        $("#format-hint").textContent = cfg.hint || "";
        onChange();
      });
    });

    $("#in-size").addEventListener("input", function () {
      state.size = Number(this.value);
      $("#size-value").textContent = state.size + " mm";
      updateSpecs();
      scheduleBuild3D();
    });

    $("#in-text").addEventListener("input", function () {
      state.text = this.value;
      updateSpecs();
      scheduleBuild3D();
    });

    $("#in-relief").addEventListener("input", function () {
      state.relief = Number(this.value);
      $("#relief-value").textContent = fmt(state.relief, 1) + " mm";
      updateSpecs();
      scheduleBuild3D();
    });

    /* descargas */
    $("#btn-png").addEventListener("click", function () { downloadImage("png"); });
    $("#btn-svg").addEventListener("click", function () { downloadImage("svg"); });
    $("#btn-3mf").addEventListener("click", download3MF);
    $("#btn-stl").addEventListener("click", downloadSTL);
  }

  /* ---------------- huecos de publicidad ---------------- */
  function initAds() {
    var dlg = $("#ad-modal");
    var toast = $("#ad-toast");

    if (dlg) {
      var close = function () { try { dlg.close(); } catch (e) { dlg.removeAttribute("open"); } };
      $("#ad-modal-close").addEventListener("click", close);
      $("#ad-modal-continue").addEventListener("click", close);
      dlg.addEventListener("click", function (e) { if (e.target === dlg) close(); });

      /* Se abre DESPUES de que la descarga haya empezado: nunca la bloquea */
      document.addEventListener("qr3d:downloaded", function (e) {
        var name = (e.detail && e.detail.name) || "";
        var n = $("#ad-modal-note");
        if (n) n.textContent = "Tu descarga de " + name + " ya ha empezado.";
        setTimeout(function () {
          if (dlg.open) return;
          try { dlg.showModal(); } catch (err) { /* dialog no soportado: sin popup */ }
        }, 350);
      });
    }

    if (toast) {
      $("#ad-toast-close").addEventListener("click", function () {
        toast.classList.remove("is-open");
        try { sessionStorage.setItem("qr3d-toast", "off"); } catch (e) {}
      });
      var off = false;
      try { off = sessionStorage.getItem("qr3d-toast") === "off"; } catch (e) {}
      if (!off) setTimeout(function () { toast.classList.add("is-open"); }, 22000);
    }
  }

  /* ---------------- arranque ---------------- */
  function boot() {
    safe(mountPalettes, "mountPalettes");
    safe(mountEmojis, "mountEmojis");
    safe(syncColorInputs, "syncColorInputs");
    safe(initControls, "initControls");
    safe(initAds, "initAds");
    safe(renderQR, "renderQR");
    safe(initLazy3D, "initLazy3D");
    document.documentElement.classList.add("is-ready");
  }

  /* sonda para verificacion automatica */
  window.__QRAPP__ = {
    state: function () {
      return {
        payload: payload(), slug: slug(), moduleCount: state.moduleCount,
        format: state.format, size: state.size, relief: state.relief,
        fg: state.fg, bg: state.bg, text: state.text,
        enabled3D: state.enabled3D, hasModel: !!state.model,
        modelInfo: state.model ? state.model.info : null,
        viewerReady: QR3D ? QR3D.isReady() : false
      };
    },
    build3D: build3D,
    enable3D: enable3D,
    set: function (k, v) { state[k] = v; },
    export3MFBlob: function () {
      return ensureModel().then(function (m) {
        return QR3D.export3MF(m, { base: state.bg, relief: state.fg });
      });
    }
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
