#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_guias.py - genera la seccion de guias (/guias/) a partir de index.html.

Cada guia es un articulo que responde una duda real de quien imprime codigos QR
en 3D. La cabecera, el pie y el hueco de anuncio se extraen de index.html (los
mismos marcadores que usa build_pages.py) y sus enlaces se pasan a rutas
absolutas, porque estas paginas viven en una subcarpeta.

Orden de ejecucion, desde la raiz del proyecto:
    python scripts/build_pages.py     # portada, satelites y pie
    python scripts/build_guias.py     # guias
    python scripts/build_pages.py     # otra vez, para que el sitemap las incluya

Para publicar una guia nueva: anadela a GUIAS (la mas reciente arriba).
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
VER = "20261016"
ROOT = os.getcwd()
AUTOR = "Julián Antonio Gaviria Jiménez"


def read(path):
    return io.open(os.path.join(ROOT, path), encoding="utf-8").read()


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    io.open(full, "w", encoding="utf-8", newline="\n").write(text)


def block(src, name):
    m = re.search(r"<!-- P:%s:START -->(.*?)<!-- P:%s:END -->" % (name, name), src, re.S)
    if not m:
        raise SystemExit("Falta el marcador P:%s en index.html" % name)
    return m.group(1).strip("\n")


def absolutizar(html):
    """Pasa href/src relativos a rutas absolutas desde la raiz del sitio."""
    html = re.sub(r'(href|src)="(?!https?:|/|#|mailto:|tel:|data:)([^"]+)"', r'\1="/\2"', html)
    # las anclas de la cabecera apuntan a secciones de la portada
    html = re.sub(r'href="#([^"]+)"', r'href="/#\1"', html)
    return html


def palabras(html):
    return len(re.sub(r"<[^>]+>", " ", html).split())


# ---------------------------------------------------------------- contenido
GUIAS = [
    {
        "slug": "qr-impreso-no-escanea",
        "title": "QR impreso en 3D que no escanea: causas y soluciones | QR3D",
        "desc": "Las 8 causas por las que un QR impreso en 3D no se lee, de la más común a la más "
                "rara, y cómo solucionar cada una antes de gastar más filamento.",
        "h1": "Por qué tu código QR impreso en 3D no se escanea (y cómo arreglarlo)",
        "fecha": "2026-10-16",
        "fecha_texto": "16 de octubre de 2026",
        "imagen": ("pieza-soporte-carta", 853, 924,
                   "Soporte de mesa con un código QR oscuro en relieve sobre una base color crema"),
        "pie": "Código oscuro sobre base clara: la combinación que mejor lee cualquier cámara. "
               "Vista del modelo 3D generado por la herramienta.",
        "intro": "Lo has impreso, ha quedado precioso, lo acercas al teléfono... y nada. Es de lo más "
                 "frustrante que te puede pasar con una impresora 3D, pero casi siempre es por una de "
                 "estas ocho causas. Están ordenadas de la más habitual a la más rara: revísalas una por "
                 "una y lo normal es que lo encuentres en las tres primeras.",
        "cuerpo": [
            """<h2>Antes de nada: prueba el código en la pantalla</h2>
<p>Abre el diseño en la pantalla del computador y escanéalo con el teléfono. Si en la pantalla
tampoco funciona, el problema no está en la impresión sino en el propio código: revisa el enlace, el
tamaño del logo o los colores antes de volver a imprimir. Si en la pantalla funciona y en la pieza no,
sigue leyendo: el problema está en el paso de la pantalla al plástico.</p>""",

            """<h2>1. Los dos colores no tienen suficiente contraste</h2>
<p>Es la causa número uno, y la menos intuitiva. La cámara del teléfono no ve el relieve: le da igual
que el código sobresalga un milímetro. Lo único que distingue son <strong>zonas claras y zonas
oscuras</strong>. Si la base y el código tienen un brillo parecido, para la cámara es una superficie
lisa, por mucho relieve que tenga.</p>
<p>El caso típico son dos colores que a la vista se distinguen perfectamente pero tienen una
luminosidad parecida: un rojo y un verde, un azul medio y un gris, un naranja y un rosa. Tú los ves
distintos porque tus ojos captan el color; la cámara, al buscar un código QR, se fija sobre todo en lo
claro y lo oscuro.</p>
<p><strong>El truco para comprobarlo:</strong> hazle una foto a la pieza, o a la pantalla con el
diseño, y pásala a blanco y negro con el editor de fotos del teléfono. Si en blanco y negro el código
se distingue mal, la cámara tampoco lo va a leer.</p>
<p><strong>La solución:</strong> código oscuro sobre base clara. Negro sobre blanco o crema es lo más
seguro; azul marino, verde oscuro o granate sobre un color claro también funcionan bien. La
herramienta calcula el contraste mientras diseñas y te avisa si baja de lo razonable.</p>""",

            """<h2>2. Los cuadritos son demasiado pequeños</h2>
<p>Un código QR está hecho de módulos, los cuadraditos que lo forman. Con una boquilla normal de
0,4 mm, si cada módulo mide menos de <strong>1,5 mm</strong> la impresora no consigue dibujar bien las
esquinas: las redondea, los bordes de cuadritos vecinos se tocan y el código se convierte en una
mancha.</p>
<p>El tamaño de cada módulo depende de dos cosas: lo grande que sea la pieza y lo largo que sea el
enlace. Cuantos más caracteres tiene el enlace, más módulos necesita el código, y si la pieza no
crece, cada uno sale más pequeño.</p>
<p><strong>La solución</strong>, por orden de preferencia:</p>
<ul>
<li><strong>Acorta el enlace.</strong> En los enlaces de redes sociales, todo lo que va detrás de un
<code>?</code> suele sobrar. Si sigue siendo largo, usa un acortador de enlaces.</li>
<li><strong>Agranda la pieza</strong> hasta que la herramienta deje de avisarte.</li>
<li>Si no puedes hacer ninguna de las dos, imprime con una <strong>boquilla de 0,25 mm</strong> y capas
finas: dibuja detalles mucho más pequeños, a costa de tardar bastante más.</li>
</ul>""",

            """<h2>3. Le falta margen alrededor</h2>
<p>Todo código QR necesita un borde liso alrededor, sin nada dibujado: lo que se llama la <strong>zona
tranquila</strong>. La norma pide un margen de cuatro módulos por cada lado. Sin ese margen, la cámara
no sabe dónde empieza y dónde acaba el código.</p>
<p>Las piezas que genera esta herramienta ya traen ese margen incluido en la base. Donde suele
romperse es después: al recortar los bordes de la pieza, al pegarla sobre un fondo con dibujos o al
colocarla pegada a otro cartel. Deja siempre un borde liso del color de la base alrededor del
código.</p>""",

            """<h2>4. Los colores están al revés</h2>
<p>El estándar QR está pensado para código oscuro sobre fondo claro. Un código claro sobre fondo oscuro
—por ejemplo blanco sobre negro, que queda muy elegante— lo leen bien la mayoría de teléfonos
modernos, pero <strong>no todos</strong>: algunos lectores antiguos y ciertas aplicaciones simplemente
no lo reconocen.</p>
<p>Si el código va a estar en un sitio público, donde lo va a escanear gente con todo tipo de
teléfonos, usa el orden clásico. Si te gusta el aspecto invertido, prueba la pieza con varios
teléfonos distintos antes de imprimir una tanda.</p>""",

            "{AD}",

            """<h2>5. El plástico brilla demasiado</h2>
<p>Los filamentos brillantes —sobre todo los llamados «seda» o «silk», y algunos PETG— reflejan la
luz. Con una lámpara encima o con sol, aparecen manchas blancas sobre el código que tapan módulos
enteros, y la cámara no puede leerlo.</p>
<p><strong>La solución:</strong> usa <strong>PLA mate</strong> al menos para la base, que es la parte
que más superficie ocupa. Si la pieza ya está impresa, prueba a escanearla inclinando un poco el
teléfono para que el reflejo no caiga encima del código.</p>""",

            """<h2>6. El cambio de filamento dejó el color sucio</h2>
<p>Si imprimes a dos colores con una impresora de un solo color, cambiando el filamento a mitad de la
pieza, la boquilla todavía tiene dentro restos del primer color cuando empieza el segundo. Las primeras
capas del relieve salen entonces de un tono intermedio, mezclado, y el contraste baja justo donde más
importa.</p>
<p><strong>La solución:</strong> después de cambiar el filamento, empuja plástico nuevo por la
boquilla hasta que salga del color limpio, sin vetas del anterior, y solo entonces reanuda. Si tienes un
sistema multicolor y ves mezcla en la pieza, aumenta el volumen de purga en el programa de impresión.
Lo explicamos paso a paso en la guía sobre
<a href="/guias/imprimir-qr-dos-colores-un-solo-color.html">cómo imprimir a dos colores con una
impresora de un solo color</a>.</p>""",

            """<h2>7. El logo del centro es demasiado grande</h2>
<p>Un código QR puede perder una parte y seguir funcionando gracias a lo que se llama
<strong>corrección de errores</strong>. En su nivel más alto puede recuperar hasta cerca de un 30 % de
información dañada, y por eso caben logos y emojis en el centro. Cuando pones algo ahí, la herramienta
sube automáticamente al nivel máximo.</p>
<p>Pero ese margen no es infinito, y en la pieza impresa se suma a todo lo demás: un poco de pérdida
por el logo, otro poco por los bordes redondeados de la impresión, otro por un reflejo... y el código
deja de leerse. Además hay tres zonas que nunca se pueden tapar: los tres cuadrados grandes de las
esquinas, que son los que permiten a la cámara encontrar el código.</p>
<p><strong>La solución:</strong> si el código falla y lleva logo, prueba primero sin él. Si sin logo
funciona, el logo era el problema: hazlo más pequeño o quítalo.</p>""",

            """<h2>8. El código se lee, pero abre otra cosa</h2>
<p>A veces el código funciona perfectamente y el problema está en el destino:</p>
<ul>
<li>Un error al copiar el enlace: una letra de más, una de menos, o la mitad del enlace sin
copiar.</li>
<li>En redes sociales, <strong>cambiaste tu nombre de usuario</strong> después de imprimir, y la
dirección antigua ya no existe.</li>
<li>En códigos de wifi, <strong>cambiaste la contraseña</strong> de la red.</li>
<li>La página a la que apuntas cambió de dirección o ya no existe.</li>
</ul>
<p>Por eso, antes de imprimir varias unidades, escanea el diseño en la pantalla y comprueba que
<strong>llega exactamente a donde quieres</strong>, no solo que «abre algo».</p>""",

            """<h2>Lista rápida antes de imprimir</h2>
<ol>
<li>El código se escanea desde la pantalla y abre el destino correcto.</li>
<li>Código oscuro sobre base clara, y se distingue bien en una foto en blanco y negro.</li>
<li>Cada cuadrito mide al menos 1,5 mm.</li>
<li>Hay un borde liso alrededor del código.</li>
<li>La base es de plástico mate.</li>
<li>Si cambias de filamento a mitad de pieza, purgas hasta que sale el color limpio.</li>
<li>Si lleva logo, has comprobado que se lee con él puesto.</li>
<li>Has impreso una unidad de prueba antes de hacer muchas.</li>
</ol>""",
        ],
        "cta": ("Deja que la herramienta lo revise por ti",
                "Mientras diseñas, el generador comprueba el contraste entre los dos colores, el tamaño "
                "de cada cuadrito y el margen alrededor del código, y te avisa antes de que imprimas.",
                [("Abrir el generador", "/", "btn--primary")]),
    },
    {
        "slug": "imprimir-qr-dos-colores-un-solo-color",
        "title": "QR a dos colores con impresora de un solo color | QR3D",
        "desc": "Con un cambio de filamento a la altura justa, cualquier impresora 3D saca un QR a dos "
                "colores. Paso a paso, y qué piezas sirven y cuáles no.",
        "h1": "Cómo imprimir un código QR a dos colores con una impresora de un solo color",
        "fecha": "2026-10-16",
        "fecha_texto": "16 de octubre de 2026",
        "imagen": ("pieza-llavero-amarillo", 838, 946,
                   "Llavero amarillo con el código QR en negro en relieve y el agujero para la anilla"),
        "pie": "Un llavero es el formato ideal para hacerlo con un solo cambio de filamento: base "
               "debajo, código encima. Vista del modelo 3D generado por la herramienta.",
        "intro": "No hace falta una impresora multicolor para sacar un código QR a dos colores. Con una "
                 "impresora normal, de las de un solo filamento, basta con un truco tan viejo como la "
                 "impresión 3D: cambiar el filamento a mitad de la pieza, justo a la altura en la que "
                 "empieza el relieve. Te explicamos cómo hacerlo, en qué formatos funciona y en cuál no.",
        "cuerpo": [
            """<h2>La idea, en una frase</h2>
<p>La impresora construye la pieza de abajo arriba, capa a capa. En un llavero o en una placa, las
capas de abajo son solo base y las de arriba son solo código. Si cambias el filamento justo en la
frontera entre las dos, la base sale de un color y el código de otro, sin hacer nada más.</p>""",

            """<h2>Primero: en qué piezas funciona y en cuál no</h2>
<p>Conviene saberlo antes de imprimir nada:</p>
<div class="table-wrap"><table>
<thead><tr><th>Formato</th><th>¿Sirve un cambio de filamento?</th><th>Por qué</th></tr></thead>
<tbody>
<tr><td>Llavero</td><td><strong>Sí</strong></td><td>El código está en la cara de arriba, que es plana</td></tr>
<tr><td>Placa de pared</td><td><strong>Sí</strong></td><td>Igual: base debajo, código encima</td></tr>
<tr><td>Soporte de mesa</td><td><strong>No</strong></td><td>El código va en una cara inclinada</td></tr>
</tbody></table></div>
<p>El soporte de mesa es la excepción porque su cara con el código está inclinada para que se lea bien
desde la silla. Eso significa que, a cualquier altura, la impresora está dibujando a la vez un trozo de
base y un trozo de código. No hay una altura en la que acabe una cosa y empiece la otra, así que un
cambio de filamento no puede separarlas. Al final de la guía te contamos qué opciones tienes para el
soporte.</p>""",

            """<h2>Paso 1: descarga el archivo</h2>
<p>Genera tu código en formato <a href="/qr-llavero.html">llavero</a> o placa y descarga el archivo
3MF. Al abrirlo en el programa de tu impresora verás dos piezas, la base y el código en relieve, que ya
encajan una sobre otra.</p>
<p>Si el programa le asigna un filamento distinto a cada pieza y tu impresora solo tiene uno, pon
<strong>las dos piezas con el mismo filamento</strong>. El color lo vas a cambiar a mano en el paso 3,
así que ahora da igual cuál elijas.</p>""",

            """<h2>Paso 2: averigua a qué altura cambiar</h2>
<p>El cambio tiene que caer justo donde termina la base y empieza el relieve. Esa altura es el grosor
de la base, y la herramienta te la muestra debajo de la vista 3D, en «Cambio de color a partir
de...».</p>
<div class="table-wrap"><table>
<thead><tr><th>Formato</th><th>Grosor de la base</th><th>El cambio va en...</th></tr></thead>
<tbody>
<tr><td>Llavero</td><td>3,0 mm</td><td>la primera capa por encima de 3,0 mm</td></tr>
<tr><td>Placa de pared</td><td>3,2 mm</td><td>la primera capa por encima de 3,2 mm</td></tr>
</tbody></table></div>
<p>Con capas de 0,2 mm, por ejemplo, en el llavero la última capa de base es la que termina en
3,0 mm y la primera de código es la que termina en 3,2 mm. El cambio tiene que hacerse <strong>antes de
empezar esa capa de 3,2 mm</strong>.</p>
<p>Si usas otra altura de capa, o una primera capa más gruesa que el resto, los números cambian un
poco. No hace falta calcularlo de cabeza: en el paso siguiente lo verás directamente en la vista
previa.</p>""",

            "{AD}",

            """<h2>Paso 3: añade el cambio de filamento en tu programa</h2>
<p>Todos los programas de impresión lo permiten. Los nombres de los menús cambian un poco según la
versión y el idioma, pero la idea es siempre la misma: <strong>lamina la pieza, abre la vista previa,
ve a la capa donde empieza el relieve y añade ahí el cambio</strong>.</p>
<ul>
<li><strong>PrusaSlicer:</strong> en la vista previa, mueve la barra vertical de capas hasta la primera
capa del relieve y pulsa el icono <strong>+</strong> que aparece junto a ella. Eso añade un cambio de
color en esa capa.</li>
<li><strong>Bambu Studio y Orca Slicer:</strong> en la vista previa, haz clic derecho sobre la barra
vertical de capas a la altura de la primera capa del relieve y elige añadir un cambio de color o una
<strong>pausa</strong>. Si tu impresora no tiene sistema multicolor, la pausa es la opción
segura.</li>
<li><strong>Cura:</strong> en el menú de extensiones, abre el post-procesado para modificar el G-code
y añade el script de <strong>cambio de filamento</strong> o el de <strong>pausa a una altura</strong>,
indicando la capa o la altura.</li>
</ul>
<p>Antes de mandar la pieza a imprimir, <strong>comprueba en la vista previa</strong> que el cambio cae
exactamente en la primera capa en la que se ven los cuadritos del código: ni una capa antes ni una
después.</p>
<div class="note note--warn"><span><b>¿Cambio de filamento o pausa?</b> El cambio de filamento (la orden
M600) hace que la impresora se detenga, aparte el cabezal y te pida que cambies el filamento. No todas
las impresoras lo admiten. Si la tuya no reacciona a él, usa la opción de pausa: se detiene igual y el
cambio lo haces tú a mano.</span></div>""",

            """<h2>Paso 4: el cambio, durante la impresión</h2>
<ol>
<li>Cuando la impresora se detenga, retira el filamento del primer color.</li>
<li>Mete el filamento del segundo color.</li>
<li><strong>Empuja plástico hasta que salga limpio.</strong> Es el paso que más se salta y el que más
estropea el resultado: la boquilla todavía tiene dentro restos del primer color, y si reanudas
enseguida, las primeras capas del código salen de un color mezclado y el contraste baja. Deja que salga
plástico hasta que no veas ni una veta del color anterior.</li>
<li>Retira con cuidado el hilo que ha salido de la boquilla, sin tocar la pieza, y reanuda.</li>
</ol>
<p>Con capas de 0,2 mm, un relieve de 1,2 mm son solo seis capas, así que la segunda parte de la
impresión es corta. Lo que sí conviene es estar cerca cuando llegue el momento del cambio, porque la
pausa no avisa con antelación.</p>""",

            """<h2>¿Y el soporte de mesa?</h2>
<p>Como hemos visto, el soporte no se puede hacer así. Estas son las opciones reales:</p>
<ul>
<li><strong>Una impresora o un sistema multicolor</strong> (AMS, MMU o similares). Es para lo que está
pensado el archivo 3MF: cada pieza ya trae su color y la máquina cambia sola.</li>
<li><strong>Imprimirlo de un solo color y pintar el relieve.</strong> Como el código sobresale, se puede
pintar solo la parte de arriba pasando por encima un rodillo de espuma pequeño con muy poca pintura
acrílica, igual que se entinta un sello. Con varias pasadas finas queda muy limpio. Prueba antes en una
pieza de descarte.</li>
<li><strong>Hacer una placa y ponerla de pie.</strong> Imprime el código en formato placa, que sí admite
el cambio de filamento, y apóyala en un atril pequeño o pégala sobre una cuña de un solo color.</li>
</ul>""",

            """<h2>Lo que necesitas, en resumen</h2>
<ul>
<li>Dos bobinas de filamento: una clara para la base y una oscura para el código. Mejor PLA mate, que
no hace reflejos (los reflejos son <a href="/guias/qr-impreso-no-escanea.html">una de las causas por las
que un QR impreso no se escanea</a>).</li>
<li>El archivo en formato llavero o placa.</li>
<li>La altura del cambio, que te da la herramienta.</li>
<li>Estar cerca de la impresora cuando llegue a esa altura.</li>
</ul>""",
        ],
        "cta": ("Genera tu pieza y te decimos dónde cambiar",
                "Elige el formato llavero o placa: debajo de la vista 3D verás la altura exacta en la "
                "que tienes que poner el cambio de filamento.",
                [("Hacer un llavero", "/qr-llavero.html", "btn--primary"),
                 ("Abrir el generador", "/", "btn--ghost")]),
    },
]


# ---------------------------------------------------------------- plantillas
def cabeza(titulo, desc, url, imagen_url, extra_ld):
    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#151b2b">

<meta property="og:type" content="article">
<meta property="og:locale" content="es_CO">
<meta property="og:site_name" content="QR3D">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{imagen}">
<meta name="twitter:card" content="summary_large_image">

<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;700&display=swap">
<link rel="stylesheet" href="/styles.css?v={ver}">

<!-- Google AdSense -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1968948020574146"
     crossorigin="anonymous"></script>
{ld}
</head>""".format(titulo=titulo, desc=desc, url=url, imagen=imagen_url, ver=VER, ld=extra_ld)


def ld(obj):
    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps(obj, ensure_ascii=False, indent=2)


def articulo(g, header, footer, anuncio, otras):
    url = "%s/guias/%s.html" % (SITE, g["slug"])
    img, w, h, alt = g["imagen"]
    img_url = "%s/assets/img/%s.webp" % (SITE, img)
    cuerpo = "\n\n".join(anuncio if b == "{AD}" else b for b in g["cuerpo"])
    minutos = max(1, round(palabras(g["intro"] + cuerpo) / 200.0))

    datos = ld({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": g["h1"],
        "description": g["desc"],
        "image": img_url,
        "datePublished": g["fecha"],
        "dateModified": g["fecha"],
        "inLanguage": "es",
        "mainEntityOfPage": url,
        "author": {"@type": "Person", "name": AUTOR, "url": SITE + "/acerca.html"},
        "publisher": {"@type": "Organization", "name": "QR3D", "url": SITE + "/",
                      "logo": {"@type": "ImageObject", "url": SITE + "/assets/favicon.svg"}},
    }) + "\n" + ld({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Guías", "item": SITE + "/guias/"},
            {"@type": "ListItem", "position": 3, "name": g["h1"], "item": url},
        ],
    })

    titulo_cta, texto_cta, botones = g["cta"]
    botones_html = "\n".join('          <a class="btn %s" href="%s">%s</a>' % (cls, href, txt)
                             for txt, href, cls in botones)
    otras_html = "\n".join(
        '        <li><a href="/guias/%s.html">%s</a></li>' % (o["slug"], o["h1"]) for o in otras)

    return cabeza(g["title"], g["desc"], url, img_url, datos) + """
<body>
<a class="skip-link" href="#main">Saltar al contenido</a>

{header}

<main id="main" class="section">
  <article class="wrap wrap--narrow prose">
    <nav class="breadcrumb" aria-label="Ruta"><a href="/">Inicio</a> &rsaquo; <a href="/guias/">Guías</a></nav>
    <span class="eyebrow">Guía</span>
    <h1 style="margin:.7rem 0 .4rem">{h1}</h1>
    <p class="article-meta">Por <a href="/acerca.html">{autor}</a> &middot; {fecha_texto} &middot; {min} min de lectura</p>
    <p class="lead" style="margin-bottom:1.6rem">{intro}</p>

    <figure class="figure-inline">
      <img src="/assets/img/{img}.webp?v={ver}" width="{w}" height="{h}" alt="{alt}" loading="eager" decoding="async">
      <figcaption>{pie}</figcaption>
    </figure>

{cuerpo}

    <div class="cta-box">
      <h3>{titulo_cta}</h3>
      <p>{texto_cta}</p>
      <div class="cta-actions">
{botones}
      </div>
    </div>

    <h2>Otras guías</h2>
    <ul>
{otras}
        <li><a href="/guias/">Todas las guías</a></li>
    </ul>
  </article>
</main>

{footer}
</body>
</html>
""".format(header=header, h1=g["h1"], autor=AUTOR, fecha_texto=g["fecha_texto"], min=minutos,
           intro=g["intro"], img=img, ver=VER, w=w, h=h, alt=alt, pie=g["pie"], cuerpo=cuerpo,
           titulo_cta=titulo_cta, texto_cta=texto_cta, botones=botones_html, otras=otras_html,
           footer=footer), minutos


def indice(header, footer, minutos):
    url = SITE + "/guias/"
    titulo = "Guías para imprimir códigos QR en 3D | QR3D"
    desc = ("Guías prácticas para imprimir códigos QR en 3D que se escanean de verdad: colores, "
            "tamaños, materiales y cómo hacerlo a dos colores con cualquier impresora.")
    tarjetas = []
    for g in GUIAS:
        img, w, h, alt = g["imagen"]
        tarjetas.append("""      <a class="guide-card" href="/guias/{slug}.html">
        <img src="/assets/img/{img}.webp?v={ver}" width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async">
        <div>
          <h2>{h1}</h2>
          <p>{desc}</p>
          <p class="article-meta">{fecha} &middot; {min} min de lectura</p>
        </div>
      </a>""".format(slug=g["slug"], img=img, ver=VER, w=w, h=h, alt=alt, h1=g["h1"],
                     desc=g["desc"], fecha=g["fecha_texto"], min=minutos[g["slug"]]))

    datos = ld({
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": titulo,
        "description": desc,
        "url": url,
        "inLanguage": "es",
        "hasPart": [{"@type": "Article", "headline": g["h1"],
                     "url": "%s/guias/%s.html" % (SITE, g["slug"])} for g in GUIAS],
    })
    return cabeza(titulo, desc, url, SITE + "/assets/img/og-cover.png", datos) + """
<body>
<a class="skip-link" href="#main">Saltar al contenido</a>

{header}

<main id="main" class="section">
  <div class="wrap wrap--narrow">
    <nav class="breadcrumb" aria-label="Ruta"><a href="/">Inicio</a> &rsaquo; Guías</nav>
    <div class="section-head">
      <span class="eyebrow">Guías</span>
      <h1 style="margin:.7rem 0 .6rem">Guías para imprimir códigos QR en 3D</h1>
      <p class="lead">Lo que hemos aprendido para que un código impreso en plástico se escanee a la primera:
        colores, tamaños, materiales y trucos de impresión. Sin relleno y con las medidas reales.</p>
    </div>
    <div class="guide-list">
{tarjetas}
    </div>
  </div>
</main>

{footer}
</body>
</html>
""".format(header=header, tarjetas="\n".join(tarjetas), footer=footer)


# ---------------------------------------------------------------- generacion
def build():
    src = read("index.html")
    header = absolutizar(block(src, "HEADER"))
    footer = absolutizar(block(src, "FOOTER"))
    anuncio = block(src, "ADINCONTENT")

    minutos = {}
    for g in GUIAS:
        otras = [o for o in GUIAS if o["slug"] != g["slug"]]
        html, m = articulo(g, header, footer, anuncio, otras)
        minutos[g["slug"]] = m
        write("guias/%s.html" % g["slug"], html)
        print("  [OK] guias/%s.html  (%d min de lectura)" % (g["slug"], m))

    write("guias/index.html", indice(header, footer, minutos))
    print("  [OK] guias/index.html  (%d guias)" % len(GUIAS))


if __name__ == "__main__":
    if not os.path.exists(os.path.join(ROOT, "index.html")):
        raise SystemExit("Ejecuta esto desde la raiz del proyecto.")
    print("Generando guias...\n")
    build()
    print("\nListo. Recuerda ejecutar build_pages.py para actualizar el sitemap.")
