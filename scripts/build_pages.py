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
VER = "20260904"
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
        "title": "Generador de QR para wifi gratis | Imagen y placa 3D",
        "desc": "Crea el código QR de tu wifi y tus invitados se conectan sin teclear la contraseña. Descárgalo en PNG o SVG, o como placa para imprimir en 3D.",
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
        "title": "QR para reseñas de Google gratis | Imagen y soporte 3D",
        "desc": "Crea el código QR que lleva directo a dejar una reseña en tu ficha de Google. Descárgalo en PNG o SVG, o como soporte de mesa para imprimir en 3D.",
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
        "title": "Llaveros con QR para imprimir en 3D gratis | QR3D",
        "desc": "Diseña tu llavero con código QR y descárgalo listo para imprimir en 3D, con el agujero para la anilla y los dos colores dentro del archivo. Gratis.",
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
    {
        "slug": "qr-carta-restaurante.html",
        "title": "QR para la carta de tu restaurante gratis | Imagen y 3D",
        "desc": "Crea el código QR de tu carta digital y descárgalo en PNG o como soporte de mesa para imprimir en 3D. Cambia la carta sin reimprimir los soportes.",
        "eyebrow": "Carta digital &middot; soporte de mesa",
        "h1": 'Generador de <em>QR para la carta</em> de tu restaurante',
        "lead": "Pega el enlace de tu carta y llévate un soporte de mesa listo para imprimir. "
                "Se limpia con un paño, no se moja y no hay que reponerlo cada semana.",
        "preset": {"mode": "link", "format": "soporte", "size": 82,
                   "text": "NUESTRA CARTA",
                   "data": "https://turestaurante.com/carta"},
        "prose_title": "Cómo montar la carta digital sin equivocarte",
        "prose": [
            ("h3", "Lo primero: a dónde debe llevar el código"),
            ("p", "Aquí es donde se decide si esto funciona o molesta. El código puede apuntar a "
                  "cualquier dirección, pero no todas dan la misma experiencia al cliente que está "
                  "sentado en tu mesa con hambre."),
            ("ul", ["<strong>Una página web con la carta:</strong> es la mejor opción. Se lee de un vistazo, "
                    "se puede ampliar y funciona igual en cualquier teléfono.",
                    "<strong>Un PDF:</strong> funciona, pero es incómodo. El cliente tiene que ampliar y "
                    "arrastrar para leer los precios, y en algunos teléfonos se descarga en vez de abrirse.",
                    "<strong>Una foto de la carta en papel:</strong> lo peor. Si no se lee bien en la pantalla, "
                    "has cambiado un papel legible por una imagen borrosa."]),
            ("h3", "El truco que te ahorra reimprimir cada temporada"),
            ("p", "Apunta el código a <strong>una dirección que tú controles</strong>, no directamente al "
                  "archivo. Si el QR lleva a <code>turestaurante.com/carta</code> y esa página muestra la "
                  "carta de cada momento, puedes cambiar los platos y los precios mil veces sin tocar los "
                  "soportes. Si en cambio el código apunta al archivo concreto de la carta de primavera, "
                  "cuando cambies de carta tendrás que imprimirlo todo otra vez."),
            ("p", "Es el error más caro y el más fácil de evitar: se decide en un minuto, antes de generar "
                  "el código."),
            ("h3", "Cuántos soportes hacen falta"),
            ("p", "Uno por mesa. Suena a mucho, pero es justo lo contrario de lo que la gente hace: poner "
                  "dos o tres en la barra y esperar que el cliente se levante. Nadie se levanta. A 4 o 5 "
                  "gramos de filamento por pieza, veinte mesas salen por menos de lo que cuesta plastificar "
                  "dos cartas."),
            ("h3", "Aguante y limpieza"),
            ("p", "El PLA aguanta perfectamente el uso de mesa y se limpia con un paño húmedo o con "
                  "desinfectante. Lo único que no soporta es el calor fuerte: no lo dejes al sol directo "
                  "en una terraza de verano ni encima de una plancha, porque el PLA empieza a deformarse "
                  "alrededor de los 60 °C. Para terrazas, PETG."),
            ("h3", "Ponle también un plan B"),
            ("p", "Habrá clientes que no sepan o no quieran escanear: gente mayor, teléfonos sin batería, "
                  "turistas sin datos. Ten dos o tres cartas en papel detrás de la barra. El QR es para "
                  "la mayoría, no para obligar a nadie."),
        ],
        "faq": [
            ("¿Necesito una página web para poner la carta?",
             "No hace falta una web completa. Vale cualquier dirección que muestre tu carta y que puedas "
             "actualizar: una página sencilla, un documento compartido o una de las plataformas de cartas "
             "digitales. Lo importante es que la dirección no cambie cuando cambies los platos."),
            ("¿Puedo cambiar la carta sin volver a imprimir los soportes?",
             "Sí, y es la gran ventaja frente al papel: si el código apunta a una dirección tuya, cambias "
             "lo que hay detrás y todos los soportes de todas las mesas quedan actualizados al instante. "
             "Por eso conviene apuntar a una página fija y no a un archivo concreto."),
            ("¿Qué tamaño de soporte funciona mejor en una mesa?",
             "Entre 75 y 90 mm de ancho. A esa medida se escanea sin acercarse desde la posición normal "
             "de alguien sentado, y la pieza no ocupa media mesa."),
            ("¿Se puede limpiar con desinfectante?",
             "Sí, sin problema. Es plástico liso: un paño con desinfectante y listo. Es una de las razones "
             "por las que compensa frente a la carta de papel plastificado, que se raya y se despega."),
            ("¿Aguanta en una terraza al sol?",
             "El PLA no: por encima de unos 60 °C empieza a ablandarse, y un salpicadero o una mesa al sol "
             "de agosto llegan ahí. Para exterior imprime en PETG, que aguanta bastante más calor."),
            ("¿Necesito dar wifi a los clientes?",
             "No es obligatorio, pero ayuda: si tu local tiene mala cobertura, un cliente sin datos no "
             "podrá abrir la carta. Muchos restaurantes ponen los dos códigos juntos, el de la wifi y el de "
             "la carta, en el mismo soporte o en dos piezas al lado."),
            ("¿Y si un cliente no sabe escanear el código?",
             "Ten siempre dos o tres cartas en papel a mano. El código digital es para agilizar a la mayoría, "
             "no para dejar fuera a quien no se maneja con el teléfono."),
            ("¿Puedo poner el logotipo de mi restaurante en el centro?",
             "Sí. Súbelo en la herramienta y aparecerá en la imagen tal cual; en la pieza impresa se "
             "convierte en una silueta en relieve del color del código. Prueba a escanear el resultado "
             "antes de imprimir todas las mesas."),
        ],
    },
    {
        "slug": "qr-whatsapp.html",
        "title": "Generador de QR para WhatsApp gratis | Imagen y 3D",
        "desc": "Crea el código QR que abre un chat de WhatsApp contigo sin que nadie guarde tu número. Descárgalo en PNG, SVG o como soporte para imprimir en 3D.",
        "eyebrow": "WhatsApp &middot; chat directo",
        "h1": 'Generador de <em>QR para WhatsApp</em> para imprimir en 3D',
        "lead": "Pon tu número y llévate un soporte listo para imprimir. Quien lo escanee abre el "
                "chat contigo directamente, sin guardar el contacto ni teclear el número.",
        "preset": {"mode": "link", "format": "soporte", "size": 78,
                   "text": "ESCRÍBENOS", "data": "https://wa.me/573001234567"},
        "prose_title": "Cómo se arma el enlace de WhatsApp",
        "prose": [
            ("p", "Esto no es un código con tu número dentro: es un enlace especial de WhatsApp que "
                  "abre la conversación contigo. La diferencia importa, porque un código que solo "
                  "contenga el número obliga a la otra persona a guardarte como contacto antes de "
                  "escribirte, y ahí se pierde a la mitad de la gente."),
            ("h3", "El formato del número"),
            ("p", "El enlace es <code>wa.me/</code> seguido de tu número <strong>con el código de "
                  "país y sin nada más</strong>: sin el signo +, sin espacios, sin guiones y sin el "
                  "cero inicial que a veces se pone delante. Un móvil colombiano queda así:"),
            ("ul", ["Número: 300 123 4567 &rarr; enlace: <code>https://wa.me/573001234567</code>",
                    "Un número español 612 345 678 &rarr; <code>https://wa.me/34612345678</code>",
                    "Un número mexicano 55 1234 5678 &rarr; <code>https://wa.me/525512345678</code>"]),
            ("p", "Es el error más común: poner el número sin el código de país. El enlace parece "
                  "correcto, el código se genera igual, y al escanearlo WhatsApp dice que el número no "
                  "es válido. Pruébalo desde tu propio teléfono antes de imprimir."),
            ("h3", "Dejar el mensaje ya escrito"),
            ("p", "Puedes hacer que el chat se abra con un texto preparado, para que la persona solo "
                  "tenga que darle a enviar. Se añade <code>?text=</code> al final: "
                  "<code>https://wa.me/573001234567?text=Hola,%20quiero%20información</code> (los "
                  "<code>%20</code> son los espacios)."),
            ("p", "Es cómodo, pero tiene un precio: alarga el enlace y eso hace el código más denso, con "
                  "los cuadritos más pequeños. Si lo usas, deja el mensaje corto y comprueba que el aviso "
                  "de la herramienta sigue en verde."),
            ("h3", "Dónde funciona mejor"),
            ("p", "En el mostrador de una tienda, en el escaparate para cuando está cerrado, en la puerta "
                  "de un taller, en una furgoneta de reparto o en una tarjeta que entregas. En todos esos "
                  "sitios la alternativa es que la persona apunte un número en el teléfono, y casi nadie "
                  "lo hace."),
            ("p", "Un consejo que no es técnico: si pones el código, contesta. Un QR de WhatsApp en la "
                  "puerta que nadie responde deja peor impresión que no tenerlo."),
        ],
        "faq": [
            ("¿Tiene que guardar mi número la otra persona?",
             "No, y esa es toda la gracia. El enlace abre la conversación contigo directamente aunque no "
             "te tenga en la agenda. Por eso funciona mucho mejor que imprimir el número a secas."),
            ("¿Funciona con WhatsApp Business?",
             "Sí, exactamente igual. El enlace apunta al número, y da lo mismo que ese número tenga la "
             "aplicación normal o la de empresa."),
            ("¿Cómo escribo mi número exactamente?",
             "Código de país y número seguidos, sin el +, sin espacios, sin guiones y sin ceros delante. "
             "Para Colombia el código es 57, para España 34 y para México 52."),
            ("¿Puedo dejar un mensaje ya escrito?",
             "Sí, añadiendo ?text= al final del enlace. Ten en cuenta que alarga el código: cuanto más "
             "largo el mensaje, más pequeños quedan los cuadritos al imprimir."),
            ("¿Y si cambio de número?",
             "El código deja de servir y hay que imprimir otro, porque el número va grabado dentro. Si tu "
             "número no es estable, es mejor apuntar el QR a una página tuya que redirija a WhatsApp: así "
             "cambias el destino sin reimprimir."),
            ("¿Sirve para un grupo de WhatsApp?",
             "No con este tipo de enlace. Los grupos usan un enlace de invitación distinto, que puedes "
             "generar desde el propio grupo y pegar aquí como cualquier otro enlace."),
            ("¿Funciona si la persona no tiene WhatsApp?",
             "Le abrirá la página de WhatsApp en el navegador invitándole a instalarlo. No es un error del "
             "código, simplemente esa persona no puede escribirte por ahí."),
        ],
    },
    {
        "slug": "qr-instagram.html",
        "title": "QR para Instagram gratis | Imagen y soporte para imprimir",
        "desc": "Crea el código QR de tu perfil de Instagram y descárgalo en PNG o SVG, o como soporte de mostrador para imprimir en 3D. Sin registro ni marcas de agua.",
        "eyebrow": "Instagram &middot; para el mostrador",
        "h1": 'Generador de <em>QR para Instagram</em> para imprimir en 3D',
        "lead": "Pega la dirección de tu perfil y llévate un soporte listo para imprimir. "
                "Un escaneo y te siguen, sin que nadie tenga que buscar tu nombre entre veinte parecidos.",
        "preset": {"mode": "link", "format": "soporte", "size": 78,
                   "text": "SÍGUENOS", "data": "https://instagram.com/tunegocio"},
        "prose_title": "Lo que hay que saber antes de imprimirlo",
        "prose": [
            ("h3", "Tu dirección de perfil"),
            ("p", "Es <code>instagram.com/</code> seguido de tu nombre de usuario, sin la arroba. Si tu "
                  "usuario es <em>@tunegocio</em>, el enlace es <code>https://instagram.com/tunegocio</code>. "
                  "Lo puedes copiar desde el navegador entrando en tu perfil."),
            ("h3", "¿Y el código que genera la propia app?"),
            ("p", "Instagram tiene su propio código dentro de la aplicación, y para compartir el perfil "
                  "de un teléfono a otro va bien. Pero es una imagen pensada para pantallas: no puedes "
                  "cambiarle los colores para que combinen con tu local, ni convertirla en una pieza "
                  "física con relieve."),
            ("p", "El código que genera esta herramienta lleva una dirección web normal, así que lo "
                  "abre la cámara de cualquier teléfono y lleva a tu perfil aunque la persona no tenga "
                  "cuenta de Instagram. Y sale como objeto impreso, con tus dos colores."),
            ("h3", "El aviso importante: no cambies de usuario"),
            ("p", "Si algún día cambias tu nombre de usuario, la dirección cambia con él y todos los "
                  "códigos impresos dejan de funcionar. Antes de imprimir una tanda, asegúrate de que el "
                  "usuario es el definitivo. Y si sospechas que lo cambiarás, apunta el QR a una página "
                  "tuya que redirija a Instagram: entonces podrás cambiar el destino cuando quieras."),
            ("h3", "¿Al perfil o a una publicación?"),
            ("p", "Casi siempre al perfil. El enlace de una publicación concreta es mucho más largo, lo "
                  "que hace el código más denso y difícil de imprimir, y además esa publicación acaba "
                  "quedando vieja mientras la pieza sigue en el mostrador."),
            ("h3", "Dónde ponerlo"),
            ("p", "En el mostrador de la tienda, en el puesto del mercado, en el estudio, junto a la caja "
                  "o en el escaparate mirando hacia fuera. La regla es sencilla: donde la gente ya está "
                  "parada y con el teléfono a mano."),
        ],
        "faq": [
            ("¿Funciona si la persona no tiene Instagram?",
             "Sí. Como el código lleva una dirección web normal, se abre en el navegador y muestra tu "
             "perfil igualmente. Si tiene la aplicación instalada, se abrirá directamente en ella."),
            ("¿Puedo usar el código que genera Instagram en la app?",
             "Para compartir de un teléfono a otro sirve. Para imprimir no tanto: es una imagen fija, no "
             "puedes elegir sus colores ni convertirla en un objeto con relieve. Esta herramienta hace un "
             "código propio con la dirección de tu perfil."),
            ("¿Y si cambio mi nombre de usuario?",
             "Los códigos ya impresos dejan de funcionar, porque la dirección incluye el usuario. Es la "
             "razón principal para no imprimir una tanda grande justo antes de un cambio de marca."),
            ("¿Puedo apuntar a una publicación concreta?",
             "Sí, pegando su enlace, pero no suele compensar: el enlace es largo, el código sale más denso "
             "y la publicación envejece mientras la pieza sigue puesta."),
            ("¿Qué tamaño va bien para un mostrador?",
             "Entre 70 y 85 mm. A esa medida se escanea de pie desde el otro lado del mostrador sin que "
             "nadie tenga que agacharse."),
            ("¿Puedo poner mi logotipo en el centro?",
             "Sí. En la imagen sale a color y en la pieza impresa se convierte en una silueta en relieve. "
             "Escanéalo una vez antes de imprimir varios, porque el logo tapa parte del código."),
        ],
    },
    {
        "slug": "qr-tiktok.html",
        "title": "QR para TikTok gratis | Imagen y placa para imprimir",
        "desc": "Crea el código QR de tu perfil de TikTok y descárgalo en PNG o SVG, o como placa para colgar impresa en 3D. Gratis y sin marcas de agua.",
        "eyebrow": "TikTok &middot; placa para colgar",
        "h1": 'Generador de <em>QR para TikTok</em> para imprimir en 3D',
        "lead": "Pega la dirección de tu perfil y llévate una placa lista para imprimir y colgar. "
                "Quien la escanee llega a tus vídeos sin buscarte a mano.",
        "preset": {"mode": "link", "format": "placa", "size": 95,
                   "text": "SÍGUENOS EN TIKTOK", "data": "https://tiktok.com/@tunegocio"},
        "prose_title": "De tu perfil a una placa colgada en la pared",
        "prose": [
            ("h3", "Tu dirección de perfil"),
            ("p", "En TikTok la arroba <strong>sí forma parte</strong> de la dirección, a diferencia de "
                  "Instagram. Queda así: <code>https://tiktok.com/@tunegocio</code>. Si te la dejas, el "
                  "enlace no lleva a ningún sitio, así que cópiala del navegador en vez de escribirla a "
                  "mano."),
            ("h3", "Por qué una placa y no un soporte de mesa"),
            ("p", "El QR de TikTok suele funcionar mejor colgado que apoyado: en la pared del local, en el "
                  "escaparate, detrás de la barra o en el panel de un puesto de feria. Es un código que la "
                  "gente escanea de pie y de paso, no sentada. Por eso esta página viene con el formato de "
                  "placa ya elegido, con sus dos agujeros para colgarla."),
            ("p", "Si prefieres tenerlo en el mostrador, cambia el formato a soporte de mesa en la propia "
                  "herramienta: el código es el mismo."),
            ("h3", "Al perfil, no a un vídeo"),
            ("p", "Es tentador apuntar al vídeo que se hizo viral, pero es mala idea por dos motivos: el "
                  "enlace de un vídeo es largo y hace el código más denso, y ese vídeo dejará de ser el "
                  "importante dentro de un mes mientras la placa sigue en la pared. Al perfil siempre."),
            ("h3", "Si cambias de usuario, el código muere"),
            ("p", "La dirección incluye tu nombre de usuario. Si lo cambias, todas las piezas impresas "
                  "dejan de llevar a ningún sitio. Es algo a tener en cuenta antes de imprimir varias "
                  "unidades, sobre todo si tu cuenta es reciente y aún estás decidiendo el nombre."),
            ("h3", "Combínalo con lo demás"),
            ("p", "Muchos negocios cuelgan dos o tres placas juntas: una para TikTok, otra para Instagram "
                  "y otra para el wifi. Si haces eso, ponles el mismo tamaño y los mismos dos colores para "
                  "que se vean como un conjunto y no como tres cosas sueltas."),
        ],
        "faq": [
            ("¿Tengo que incluir la arroba en la dirección?",
             "Sí. En TikTok la dirección del perfil lleva la arroba dentro: tiktok.com/@tuusuario. Sin "
             "ella el enlace no funciona. Lo más seguro es copiarla desde el navegador."),
            ("¿Funciona si quien escanea no tiene TikTok?",
             "Sí, se abre el perfil en el navegador. Si tiene la aplicación instalada, normalmente se abre "
             "directamente en ella."),
            ("¿Puedo usar el código que genera TikTok dentro de la app?",
             "Para compartir entre teléfonos sirve. Para imprimir no: es una imagen fija con los colores "
             "de la aplicación y no se puede convertir en una pieza con relieve y tus colores."),
            ("¿Mejor apuntar a un vídeo concreto?",
             "No lo recomendamos. El enlace es largo, el código sale más denso y el vídeo se queda "
             "desactualizado mientras la placa sigue colgada."),
            ("¿De qué tamaño hago la placa?",
             "Entre 90 y 110 mm si va en una pared y la gente la escanea desde medio metro o menos. Si va "
             "más alta o más lejos, agranda la pieza."),
            ("¿Cómo la cuelgo?",
             "Trae dos agujeros arriba para tornillos o alcayatas. Para una pared lisa o un escaparate "
             "también aguanta con cinta de doble cara, porque la pieza pesa muy poco."),
        ],
    },
]

HOME = {"slug": "index.html", "nav": "El generador completo",
        "navdesc": "Los tres formatos, todos los estilos y la guía de impresión."}
NAV_DESC = {
    "qr-wifi.html": "El código de tu red en una placa, para apartamentos y locales.",
    "qr-resenas-google.html": "Soporte de mesa que lleva directo a valorar tu negocio.",
    "qr-llavero.html": "Con su agujero para la anilla, para eventos y mascotas.",
    "qr-carta-restaurante.html": "Soporte de mesa con el enlace a tu carta digital.",
    "qr-whatsapp.html": "Abre el chat contigo sin guardar tu numero.",
    "qr-instagram.html": "Tu perfil en el mostrador, para que te sigan al momento.",
    "qr-tiktok.html": "Placa para colgar con el enlace a tus videos.",
}
NAV_LABEL = {
    "qr-wifi.html": "QR de wifi",
    "qr-resenas-google.html": "QR para reseñas de Google",
    "qr-llavero.html": "Llavero con QR",
    "qr-carta-restaurante.html": "QR para la carta",
    "qr-whatsapp.html": "QR para WhatsApp",
    "qr-instagram.html": "QR para Instagram",
    "qr-tiktok.html": "QR para TikTok",
}
NAV_ICON = {
    "index.html": "&#128736;&#65039;",
    "qr-wifi.html": "&#128246;",
    "qr-resenas-google.html": "&#11088;",
    "qr-llavero.html": "&#128273;",
    "qr-carta-restaurante.html": "&#127869;&#65039;",
    "qr-whatsapp.html": "&#128172;",
    "qr-instagram.html": "&#128248;",
    "qr-tiktok.html": "&#127925;",
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


# imagen propia de cada pagina: (archivo, ancho, alto, alt, pie)
IMAGENES = {
    "qr-wifi.html": ("pieza-placa-wifi", 575, 709,
        "Placa de pared lila con el codigo de la wifi en morado, dos agujeros para colgar y el texto WIFI",
        "Placa de 95 mm con el c\u00f3digo de una red wifi. Los dos agujeros para colgarla vienen ya en el archivo."),
    "qr-resenas-google.html": ("pieza-soporte-resenas", 840, 883,
        "Soporte de mesa azul marino con una estrella en relieve en el centro del codigo",
        "Soporte de 82 mm con la estrella en relieve y el texto en la parte de abajo, tal y como sale del archivo."),
    "qr-llavero.html": ("pieza-llavero-amarillo", 838, 946,
        "Llavero amarillo con el codigo QR en negro en relieve y el agujero para la anilla",
        "Llavero de 60 mm en negro sobre amarillo: el m\u00e1ximo contraste posible para una pieza peque\u00f1a."),
    "qr-carta-restaurante.html": ("pieza-soporte-carta", 853, 924,
        "Soporte de mesa con el codigo en relieve oscuro sobre base crema y el texto NUESTRA CARTA",
        "Soporte de 82 mm inclinado a 60 grados. La cara del c\u00f3digo mira hacia arriba y se imprime sin soportes."),
    "qr-whatsapp.html": ("pieza-soporte-whatsapp", 800, 897,
        "Soporte de mesa verde oscuro con un bocadillo de chat en el centro y el texto ESCRIBENOS",
        "Soporte de 78 mm para el mostrador, con el emoji de conversaci\u00f3n convertido en silueta en relieve."),
    "qr-instagram.html": ("pieza-soporte-instagram", 756, 832,
        "Soporte de mesa granate sobre base rosa palido con una camara en relieve y el texto SIGUENOS",
        "Soporte de 78 mm en estilo elegante: los cuadritos se unen en trazos redondeados."),
    "qr-tiktok.html": ("pieza-placa-social", 561, 721,
        "Placa de pared color arena con el codigo en rojo teja y el texto SIGUENOS en relieve",
        "Placa de 95 mm para colgar en la pared o el escaparate, con sus dos agujeros arriba."),
}


def figura(slug):
    """Vista 3D propia de la pieza. No es una fotografia y el pie lo deja claro."""
    d = IMAGENES.get(slug)
    if not d:
        return ""
    f, w, h, alt, pie = d
    return ('      <figure class="figure-inline">\n'
            '        <img src="assets/img/%s.webp?v=20260904" width="%d" height="%d"\n'
            '             alt="%s" loading="lazy" decoding="async">\n'
            '        <figcaption>%s Es una vista del modelo 3D que genera esta web, no una fotograf&iacute;a.</figcaption>\n'
            '      </figure>' % (f, w, h, alt, pie))


def footer_tools():
    """Lista de herramientas del pie: se genera con TODAS las paginas, para que
    anadir una nueva no deje el pie desactualizado."""
    rows = ['        <ul>',
            '          <li><a href="index.html">Generador completo</a></li>']
    for p in PAGES:
        rows.append('          <li><a href="%s">%s</a></li>' % (p["slug"], NAV_LABEL[p["slug"]]))
    rows.append('        </ul>')
    return "\n".join(rows)


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

    footer = replace_block(parts["FOOTER"], "FOOTERTOOLS", footer_tools())

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
{figura}
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
           figura=figura(page["slug"]),
           adincontent=parts["ADINCONTENT"],
           faq=faq_html(page["faq"]), more=more_tools(page["slug"]),
           footer=footer, overlays=parts["OVERLAYS"], scripts=parts["SCRIPTS"])
        write(page["slug"], html)
        print("  [OK] %s" % page["slug"])

    # la portada tambien enlaza a las nuevas paginas
    src = replace_block(src, "MORE", more_tools("index.html"))
    src = replace_block(src, "FOOTERTOOLS", footer_tools())
    write("index.html", src)
    print("  [OK] index.html (bloque de mas herramientas)")

    # sitemap con todas las paginas
    urls = (["/"] + ["/" + p["slug"] for p in PAGES]
            + ["/acerca.html", "/contacto.html", "/privacidad.html", "/aviso-legal.html"])
    rows = []
    for u in urls:
        if u == "/":
            prio = "1.0"
        elif "legal" in u or "privacidad" in u:
            prio = "0.2"
        elif u in ("/acerca.html", "/contacto.html"):
            prio = "0.4"
        else:
            prio = "0.8"
        freq = "weekly" if prio != "0.2" else "yearly"
        rows.append("  <url>\n    <loc>%s%s</loc>\n    <lastmod>2026-09-04</lastmod>\n"
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
