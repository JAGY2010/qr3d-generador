#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_pages.py - genera las paginas satelite del sitio a partir de index.html.

Cada pagina apunta a UNA busqueda concreta ("qr wifi", "qr resenas de Google",
"llavero qr") y trae la MISMA herramienta ya preconfigurada para ese caso. La
herramienta, la cabecera, el pie, los huecos de anuncio y los scripts se
extraen de index.html entre marcadores <!-- P:BLOQUE:START/END -->, asi que
nunca se desincronizan: se toca index.html y se vuelve a ejecutar esto.

Es una herramienta de desarrollo. NO se despliega y la web no depende de ella:
lo que se publica son los .html ya generados.

    python scripts/build_pages.py        # desde la raiz del proyecto
"""
import io
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SITE = "https://lexasylum.com"
VER = "20260819"
ROOT = os.getcwd()


# ---------------------------------------------------------------- utilidades
def read(path):
    return io.open(os.path.join(ROOT, path), encoding="utf-8").read()


def write(path, text):
    io.open(os.path.join(ROOT, path), "w", encoding="utf-8", newline="\n").write(text)


def block(src, name):
    m = re.search(r"<!-- P:%s:START -->(.*?)<!-- P:%s:END -->" % (name, name), src, re.S)
    if not m:
        raise SystemExit("Falta el marcador P:%s en index.html" % name)
    return m.group(1).strip("\n")


def replace_block(src, name, content):
    return re.sub(
        r"(<!-- P:%s:START -->).*?(<!-- P:%s:END -->)" % (name, name),
        lambda m: m.group(1) + "\n" + content + "\n  " + m.group(2),
        src, flags=re.S)


# ---------------------------------------------------------------- contenido
PAGES = [
    {
        "slug": "qr-wifi.html",
        "title": "QR de wifi para imprimir en 3D | QR3D",
        "desc": "Crea el codigo QR de tu wifi y descargalo en 3MF a dos colores para "
                "imprimirlo en 3D. Tus huespedes se conectan sin teclear la contrasena.",
        "eyebrow": "Wifi &middot; sin dictar contrase&ntilde;as",
        "h1": 'Generador de <em>QR de wifi</em> para imprimir en 3D',
        "lead": "Escribe el nombre de tu red y la contrase&ntilde;a, y ll&eacute;vate una placa lista "
                "para imprimir y colgar. Quien la escanee se conecta solo, sin preguntarte la clave.",
        "preset": {"mode": "wifi", "format": "placa", "size": 95, "text": "WIFI", "data": None},
        "prose_title": "Todo lo que conviene saber del QR de wifi",
        "prose": [
            ("p", "Un código QR de wifi no es un enlace: es una etiqueta con el nombre de la red, "
                  "el tipo de seguridad y la contraseña, escritos en un formato estándar que "
                  "los teléfonos reconocen. Al escanearlo, el aparato ofrece conectarse a esa red "
                  "y lo hace solo. Nadie teclea nada."),
            ("h3", "Qué seguridad elegir"),
            ("p", "En la herramienta tienes tres opciones y casi siempre es la primera. "
                  "<strong>WPA / WPA2 / WPA3</strong> cubre prácticamente todos los routers de los "
                  "últimos quince años. <strong>WEP</strong> es de routers muy antiguos y hoy se "
                  "considera inseguro. <strong>Red abierta</strong> es para wifis sin contraseña, "
                  "típicas de zonas comunes."),
            ("h3", "Qué formato imprimir según dónde va"),
            ("ul", ["<strong>Placa de pared:</strong> lo habitual en apartamentos turísticos y hoteles. "
                    "Se atornilla o se pega junto al router, en el recibidor o dentro del armario.",
                    "<strong>Soporte de mesa:</strong> para la mesa de la habitación, la barra de un bar "
                    "o la recepción. Se ve sin buscarlo.",
                    "<strong>Llavero:</strong> para entregarlo con las llaves del apartamento. Ojo: la "
                    "contraseña alarga el código y en una pieza pequeña los cuadritos quedan "
                    "diminutos. La herramienta te avisa si pasa."]),
            ("h3", "El detalle que arruina la pieza"),
            ("p", "Una contraseña larga genera un código con muchos módulos, y cuantos más "
                  "módulos, más pequeño es cada cuadrito. Por debajo de 1,5 mm la boquilla los "
                  "redondea y el código deja de leerse. Si tu clave es de esas de veinte caracteres "
                  "con símbolos, agranda la placa hasta que el aviso se ponga en verde: es literalmente "
                  "la diferencia entre una pieza que funciona y una que no."),
        ],
        "faq": [
            ("¿Funciona en iPhone y en Android?",
             "Sí, en los dos y sin instalar ninguna aplicación. La cámara de iPhone lo reconoce "
             "desde iOS 11 y Android desde hace años. Al enfocar el código aparece un aviso para "
             "unirse a la red."),
            ("¿Y si cambio la contraseña del wifi?",
             "La placa deja de servir y hay que imprimir otra: el código lleva la clave grabada dentro. "
             "Por eso, si sueles cambiarla, imprime la pieza en un formato barato o déjala en un sitio "
             "fácil de sustituir."),
            ("¿Es seguro poner la contraseña en un código QR?",
             "Cualquiera que vea el código puede extraer la contraseña, igual que si la tuvieras "
             "escrita en un papel. Para una red de invitados es perfecto. Para tu red principal, donde "
             "están tus dispositivos y tus archivos compartidos, es mejor crear una red de invitados "
             "aparte en el router y hacer el código de esa."),
            ("¿Sirve para una red oculta?",
             "No. Las redes que no emiten su nombre necesitan un dato extra que esta herramienta no "
             "genera. Si tu red está oculta, lo más práctico es hacerla visible o crear una "
             "red de invitados normal."),
            ("¿Puedo usar tildes o la ñ en el nombre de la red?",
             "Sí, y también símbolos como punto y coma o comillas: la herramienta los escapa "
             "como manda el estándar. Aún así, si vas a crear la red desde cero, un nombre "
             "sencillo genera un código más pequeño y más fácil de imprimir."),
            ("¿De qué tamaño hago la placa?",
             "Entre 90 y 110 mm de ancho va bien para colgarla en una pared y escanearla desde medio metro. "
             "Fija el tamaño mirando el aviso de milimetros por cuadrito: mientras esté por encima "
             "de 1,5 mm vas sobrado."),
        ],
    },
    {
        "slug": "qr-resenas-google.html",
        "title": "QR para reseñas de Google en 3D | QR3D",
        "desc": "Genera el codigo QR que lleva directo a dejar una resena en tu ficha de Google "
                "y descargalo listo para imprimir en 3D, en un soporte de mesa a dos colores.",
        "eyebrow": "Reseñas &middot; soporte de mesa",
        "h1": 'Generador de <em>QR para reseñas de Google</em>',
        "lead": "Pega el enlace de reseñas de tu ficha de empresa y llévate un soporte de mesa "
                "listo para imprimir. El cliente escanea, escribe y se va.",
        "preset": {"mode": "link", "format": "soporte", "size": 82,
                   "text": "DÉJANOS TU RESEÑA",
                   "data": "https://g.page/r/TU-CODIGO/review"},
        "prose_title": "Cómo montar tu QR de reseñas paso a paso",
        "prose": [
            ("h3", "1. Consigue tu enlace de reseñas"),
            ("p", "No sirve el enlace de tu ficha ni el de tu web: necesitas el que abre directamente "
                  "la ventana para escribir la reseña. Se saca desde tu <strong>Perfil de Empresa "
                  "de Google</strong>, en la opción <strong>Pedir reseñas</strong>, que te da un "
                  "enlace corto listo para copiar."),
            ("p", "Si no lo encuentras, hay un camino alternativo: busca tu negocio en Google, entra en "
                  "sus reseñas, pulsa <em>Escribir una reseña</em> y copia la dirección que "
                  "aparece en la barra del navegador. Ese enlace también vale."),
            ("h3", "2. Comprueba que el enlace hace lo que debe"),
            ("p", "Antes de imprimir nada, ábrelo en tu teléfono. Tiene que saltar directo al "
                  "cuadro de las estrellas. Si abre tu ficha y hay que buscar el botón, has copiado "
                  "el enlace equivocado y vas a perder la mitad de las reseñas por el camino: cada "
                  "clic de más es gente que se cansa."),
            ("h3", "3. Ponlo donde la gente está esperando"),
            ("p", "El mejor momento para pedir una reseña es cuando el cliente ya está contento y "
                  "sin prisa: en la mesa después de comer, en el mostrador mientras cobras, en la sala "
                  "de espera. Por eso el soporte de mesa funciona mejor que un cartel en la pared: está "
                  "a la altura de los ojos y a un brazo de distancia."),
            ("h3", "Qué escribir en el texto en relieve"),
            ("p", "Tienes 22 caracteres. Funciona mejor una petición directa y humana que el nombre del "
                  "negocio, que ya saben dónde están. Ideas que caben: "
                  "<strong>Déjanos tu reseña</strong>, <strong>¿Qué tal estuvo?</strong>, "
                  "<strong>Cuéntanos qué tal</strong> o <strong>Gracias por tu opinión</strong>."),
        ],
        "faq": [
            ("¿Es legal pedir reseñas a mis clientes?",
             "Pedirlas sí, y Google lo recomienda. Lo que sus normas prohíben es "
             "<strong>incentivarlas</strong>: no puedes ofrecer un descuento, un regalo ni un sorteo a "
             "cambio de una reseña. Un soporte en la mesa que invita a opinar está dentro de las "
             "reglas; un cartel que diga «reseña de 5 estrellas y te invitamos al café», no."),
            ("¿Puedo hacer que solo los clientes contentos dejen reseña?",
             "No, y además va contra las normas de Google. Filtrar a la gente según si va a hablar "
             "bien o mal (lo que se llama «filtrado de reseñas») puede costarte que Google "
             "actúe contra tu ficha. El QR lleva a todo el mundo al mismo sitio."),
            ("¿Cuánto sube esto las reseñas de verdad?",
             "Depende de tu negocio, pero el salto grande viene de quitar fricción: la mayoría de "
             "clientes contentos no deja reseña simplemente porque implica sacar el teléfono, "
             "buscarte y navegar. Un código a un brazo de distancia elimina esos tres pasos."),
            ("¿Dónde lo coloco si tengo un local pequeño?",
             "En el mostrador, junto a la caja, orientado hacia el cliente y no hacia ti. Si tienes mesas, "
             "una unidad por mesa rinde mucho más que una sola en la entrada."),
            ("¿Qué tamaño de soporte funciona mejor?",
             "Entre 75 y 90 mm de ancho. A esa medida se escanea cómodamente desde la distancia normal "
             "de una mesa y la pieza sigue siendo discreta."),
            ("¿Y si cambio de local o de nombre?",
             "El enlace de reseñas sigue apuntando a tu ficha aunque cambies la dirección o el "
             "nombre dentro de ella, así que la pieza te sirve igual. Solo tendrías que reimprimir "
             "si creas una ficha nueva desde cero."),
        ],
    },
    {
        "slug": "qr-llavero.html",
        "title": "Llavero con código QR para imprimir en 3D | QR3D",
        "desc": "Disena un llavero con tu codigo QR y descargalo en 3MF a dos colores, con el agujero "
                "para la anilla ya hecho. Ideal para eventos, bodas, ferias y mascotas.",
        "eyebrow": "Llavero &middot; con agujero para la anilla",
        "h1": 'Llavero con <em>código QR</em> para imprimir en 3D',
        "lead": "Pon tu enlace, escribe un texto corto y llévate el llavero listo para imprimir, "
                "con su agujero para la anilla y los dos colores dentro del archivo.",
        "preset": {"mode": "link", "format": "llavero", "size": 58, "text": "",
                   "data": "https://tunegocio.com"},
        "prose_title": "La regla de oro del llavero: enlace corto",
        "prose": [
            ("p", "En una pieza pequeña hay muy poco sitio, y ahí es donde se estrellan casi todos los "
                  "intentos. Estas medidas están sacadas de la propia herramienta, no son teoría:"),
            ("ul", ["<code>tunegocio.com</code> (21 caracteres) genera un código de 25 cuadritos. "
                    "En un llavero de 58 mm cada cuadrito mide <strong>1,76 mm</strong>: perfecto.",
                    "<code>instagram.com/tunegocio</code> (31 caracteres) sube a 29 cuadritos. "
                    "En esos mismos 58 mm cada uno baja a <strong>1,57 mm</strong>: sigue funcionando, "
                    "pero ya va justo.",
                    "Ese mismo enlace en un llavero de 48 mm deja los cuadritos en "
                    "<strong>1,30 mm</strong>, por debajo del mínimo. Impreso queda una mancha que no "
                    "escanea nadie."]),
            ("p", "La conclusión es simple: cada carácter que quitas del enlace es tamaño que ganas en "
                  "el llavero. Si tu destino es largo, acórtalo antes de generar el código; y si no puedes, "
                  "agranda la pieza hasta que el aviso deje de estar en rojo. Con el aviso rojo no imprimas: "
                  "estarás gastando filamento en algo que no se lee."),
            ("h3", "Para qué se usan"),
            ("ul", ["<strong>Bodas y eventos:</strong> un llavero por invitado con el QR al álbum de fotos "
                    "compartido. Recuerdo y enlace en la misma pieza.",
                    "<strong>Ferias y congresos:</strong> tu perfil profesional o tu catálogo. Se reparte "
                    "mejor que una tarjeta y no acaba en la basura del hotel.",
                    "<strong>Mascotas:</strong> una chapa para el collar con el QR a una página con tu "
                    "teléfono. Quien encuentre al animal escanea y te llama, sin que tu número quede "
                    "grabado a la vista.",
                    "<strong>Negocios locales:</strong> el QR a tu menú, tu tienda o tu WhatsApp, "
                    "regalado con cada compra."]),
            ("h3", "Ajustes de impresión"),
            ("p", "El llavero sale con 3 mm de grosor, que aguanta el bolsillo sin partirse. Con 0,2 mm de "
                  "altura de capa y 15 % de relleno tarda entre veinte y cuarenta minutos. Si vas a hacer "
                  "muchos, colócalos en cuadrícula sobre la cama: caben fácilmente diez o doce "
                  "en una impresora de tamaño normal y toda la tanda sale en una noche."),
        ],
        "faq": [
            ("¿Se rompe con el uso?",
             "Con 3 mm de grosor y PLA normal aguanta bien el trajín de un llavero. Si va a llevar mucho "
             "castigo, imprime en PETG: es más flexible y no se vuelve quebradizo con el calor del coche."),
            ("¿Qué anilla le pongo?",
             "El agujero está pensado para una anilla estándar de 20 a 25 mm, de las que se venden "
             "por cientos en cualquier bazar o tienda de manualidades."),
            ("¿Puedo ponerlo en el collar de mi perro?",
             "Sí, es uno de los usos más prácticos. Apunta el QR a una página con tu "
             "teléfono en vez de grabar el número: así puedes cambiarlo sin reimprimir la chapa. "
             "Para el collar, PETG aguanta mejor la lluvia y el sol que el PLA."),
            ("¿Cuánto material gasta?",
             "Muy poco: un llavero de 48 mm ronda los 4 o 5 gramos. Con una bobina de un kilo salen del orden "
             "de doscientas unidades contando el segundo color."),
            ("¿Puedo venderlos?",
             "Sí. Los archivos que generas son tuyos y no llevan ninguna licencia ni marca de agua. "
             "Puedes imprimirlos y venderlos sin pedir permiso."),
            ("¿Se puede escanear un llavero tan pequeño?",
             "Sí, siempre que el aviso de milimetros por cuadrito esté en verde. La distancia de "
             "lectura es corta, unos diez centímetros, pero para un llavero que se coge con la mano es "
             "justo lo que se necesita."),
        ],
    },
]

HOME = {"slug": "index.html", "nav": "El generador completo",
        "navdesc": "Los tres formatos, todos los estilos y la guía de impresión."}
NAV_DESC = {
    "qr-wifi.html": "El código de tu red en una placa, para apartamentos y locales.",
    "qr-resenas-google.html": "Soporte de mesa que lleva directo a valorar tu negocio.",
    "qr-llavero.html": "Con su agujero para la anilla, para eventos y mascotas.",
}
NAV_LABEL = {
    "qr-wifi.html": "QR de wifi",
    "qr-resenas-google.html": "QR para reseñas de Google",
    "qr-llavero.html": "Llavero con QR",
}
NAV_ICON = {
    "index.html": "&#128736;&#65039;",
    "qr-wifi.html": "&#128246;",
    "qr-resenas-google.html": "&#11088;",
    "qr-llavero.html": "&#128273;",
}


# ---------------------------------------------------------------- preset
def apply_preset(tool, preset):
    """Deja la herramienta preconfigurada para el caso de esta pagina."""
    t = tool

    if preset.get("data") is not None:
        t = re.sub(r'(id="in-data" value=")[^"]*(")',
                   lambda m: m.group(1) + preset["data"] + m.group(2), t)

    if preset.get("mode") == "wifi":
        t = t.replace('id="tab-link" aria-selected="true"', 'id="tab-link" aria-selected="false"')
        t = t.replace('id="tab-wifi" aria-selected="false"', 'id="tab-wifi" aria-selected="true"')
        t = t.replace('<div id="pane-link" role="tabpanel" aria-labelledby="tab-link"',
                      '<div id="pane-link" role="tabpanel" aria-labelledby="tab-link" hidden')
        t = t.replace('<div id="pane-wifi" role="tabpanel" aria-labelledby="tab-wifi" hidden',
                      '<div id="pane-wifi" role="tabpanel" aria-labelledby="tab-wifi"')

    fmt = preset.get("format")
    if fmt and fmt != "soporte":
        t = t.replace('data-format="soporte" aria-pressed="true"', 'data-format="soporte" aria-pressed="false"')
        t = t.replace('data-format="%s" aria-pressed="false"' % fmt, 'data-format="%s" aria-pressed="true"' % fmt)

    limits = {"soporte": (55, 130), "llavero": (35, 80), "placa": (60, 160)}
    lo, hi = limits.get(fmt or "soporte", (55, 130))
    size = preset.get("size", 78)
    t = re.sub(r'(id="in-size" min=")\d+(" max=")\d+(" step="1" value=")\d+(")',
               lambda m: "%s%d%s%d%s%d%s" % (m.group(1), lo, m.group(2), hi, m.group(3), size, m.group(4)), t)
    t = re.sub(r'(id="size-value"[^>]*>)[^<]*(</b>)',
               lambda m: m.group(1) + str(size) + " mm" + m.group(2), t)

    text = preset.get("text", "")
    t = re.sub(r'(id="in-text" maxlength="22")',
               lambda m: m.group(1) + (' value="%s"' % text if text else ""), t)
    return t


# ---------------------------------------------------------------- plantillas
def more_tools(current):
    """Bloque «mas herramientas»: enlaza las otras paginas del sitio."""
    items = [{"slug": "index.html", "label": HOME["nav"], "desc": HOME["navdesc"]}]
    for p in PAGES:
        items.append({"slug": p["slug"], "label": NAV_LABEL[p["slug"]], "desc": NAV_DESC[p["slug"]]})
    cards = []
    for it in items:
        if it["slug"] == current:
            continue
        cards.append(
            '        <a class="use" href="%s">\n'
            '          <span class="ico" aria-hidden="true">%s</span>\n'
            '          <div><h3>%s</h3><p>%s</p></div>\n'
            '        </a>' % (it["slug"], NAV_ICON[it["slug"]], it["label"], it["desc"]))
    return (
        '  <section class="section" id="mas-herramientas" style="background:var(--surface-2)">\n'
        '    <div class="wrap">\n'
        '      <div class="section-head">\n'
        '        <span class="eyebrow">M&aacute;s herramientas</span>\n'
        '        <h2>Otros c&oacute;digos QR listos para imprimir</h2>\n'
        '        <p class="lead">La misma herramienta, preparada para cada caso.</p>\n'
        '      </div>\n'
        '      <div class="uses">\n' + "\n".join(cards) + "\n"
        '      </div>\n'
        '    </div>\n'
        '  </section>')


def prose_html(items):
    out = []
    for kind, val in items:
        if kind == "p":
            out.append("      <p>%s</p>" % val)
        elif kind == "h3":
            out.append("      <h3>%s</h3>" % val)
        elif kind == "ul":
            out.append("      <ul>")
            for li in val:
                out.append("        <li>%s</li>" % li)
            out.append("      </ul>")
    return "\n".join(out)


def faq_html(items):
    out = []
    for q, a in items:
        out.append('        <details class="acc"><summary>%s</summary>\n'
                   '          <div><p>%s</p></div>\n'
                   '        </details>' % (q, a))
    return "\n".join(out)


def faq_jsonld(items):
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": re.sub(r"<[^>]+>", "", q),
             "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}}
            for q, a in items
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def app_jsonld(page):
    data = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": re.sub(r"<[^>]+>", "", page["h1"]),
        "url": SITE + "/" + page["slug"],
        "applicationCategory": "DesignApplication",
        "operatingSystem": "Cualquiera (navegador web)",
        "description": page["desc"],
        "inLanguage": "es",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "COP"},
        "isPartOf": {"@type": "WebSite", "name": "QR3D", "url": SITE + "/"},
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- generacion
def build():
    src = read("index.html")
    parts = {name: block(src, name) for name in
             ("HEADASSETS", "HEADER", "BADGES", "TOOL", "ADLEADER", "ADINCONTENT",
              "FOOTER", "OVERLAYS", "SCRIPTS")}

    # Las paginas satelite tienen #herramienta, #guia, #faq y #mas-herramientas
    # propios; solo las secciones que viven unicamente en la portada se redirigen.
    header = parts["HEADER"]
    for anchor in ("#como-funciona", "#ideas"):
        header = header.replace('href="%s"' % anchor, 'href="index.html%s"' % anchor)

    for page in PAGES:
        tool = apply_preset(parts["TOOL"], page["preset"])
        html = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{site}/{slug}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#151b2b">

<meta property="og:type" content="website">
<meta property="og:locale" content="es_CO">
<meta property="og:site_name" content="QR3D">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{site}/{slug}">
<meta property="og:image" content="{site}/assets/img/og-cover.png">
<meta name="twitter:card" content="summary_large_image">

{headassets}

<script type="application/ld+json">
{appld}
</script>
<script type="application/ld+json">
{faqld}
</script>
</head>
<body>
<a class="skip-link" href="#herramienta">Saltar a la herramienta</a>

{header}

<main id="main">

  <section class="hero" id="herramienta">
    <div class="wrap">
      <div class="hero-head">
        <span class="eyebrow">{eyebrow}</span>
        <h1>{h1}</h1>
        <p class="lead">{lead}</p>
{badges}
      </div>

{tool}

{adleader}
    </div>
  </section>

  <section class="section" id="guia">
    <div class="wrap wrap--narrow prose">
      <div class="section-head">
        <span class="eyebrow">Gu&iacute;a</span>
        <h2>{prose_title}</h2>
      </div>
{prose}

{adincontent}
    </div>
  </section>

  <section class="section" id="faq" style="background:var(--surface-2)">
    <div class="wrap wrap--narrow">
      <div class="section-head">
        <span class="eyebrow">Dudas</span>
        <h2>Preguntas frecuentes</h2>
      </div>
      <div class="faq">
{faq}
      </div>
    </div>
  </section>

  <!-- P:MORE:START -->
{more}
  <!-- P:MORE:END -->
</main>

{footer}

{overlays}

{scripts}
</body>
</html>
""".format(title=page["title"], desc=page["desc"], site=SITE, slug=page["slug"],
           headassets=parts["HEADASSETS"], appld=app_jsonld(page), faqld=faq_jsonld(page["faq"]),
           header=header, eyebrow=page["eyebrow"], h1=page["h1"], lead=page["lead"],
           badges=parts["BADGES"], tool=tool, adleader=parts["ADLEADER"],
           prose_title=page["prose_title"], prose=prose_html(page["prose"]),
           adincontent=parts["ADINCONTENT"],
           faq=faq_html(page["faq"]), more=more_tools(page["slug"]),
           footer=parts["FOOTER"], overlays=parts["OVERLAYS"], scripts=parts["SCRIPTS"])
        write(page["slug"], html)
        print("  [OK] %s" % page["slug"])

    # la portada tambien enlaza a las nuevas paginas
    src = replace_block(src, "MORE", more_tools("index.html"))
    write("index.html", src)
    print("  [OK] index.html (bloque de mas herramientas)")

    # sitemap con todas las paginas
    urls = ["/"] + ["/" + p["slug"] for p in PAGES] + ["/privacidad.html", "/aviso-legal.html"]
    rows = []
    for u in urls:
        prio = "1.0" if u == "/" else ("0.2" if "legal" in u or "privacidad" in u else "0.8")
        freq = "weekly" if prio != "0.2" else "yearly"
        rows.append("  <url>\n    <loc>%s%s</loc>\n    <lastmod>2026-08-19</lastmod>\n"
                    "    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>"
                    % (SITE, u, freq, prio))
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "\n".join(rows) + "\n</urlset>\n")
    print("  [OK] sitemap.xml (%d URLs)" % len(urls))


if __name__ == "__main__":
    if not os.path.exists(os.path.join(ROOT, "index.html")):
        raise SystemExit("Ejecuta esto desde la raiz del proyecto.")
    print("Generando paginas satelite...\n")
    build()
    print("\nListo.")
