# QR3D — generador de códigos QR para imprimir en 3D

Web-herramienta 100 % del lado del cliente: el visitante pega un enlace, diseña
su código QR y se descarga tanto la imagen (PNG / SVG) como un objeto listo para
imprimir en 3D — **3MF con los dos colores guardados dentro del archivo**, y STL
como alternativa para impresoras antiguas.

No hay servidor de procesamiento, ni cuentas, ni claves de API: todo ocurre en el
navegador del visitante.

## Qué hace

- **Contenido:** enlace / texto o credenciales de wifi (`WIFI:T:...;S:...;P:...;;`).
- **Diseño:** 4 estilos (clásico, redondeado, puntos, elegante), dos colores y
  logo o emoji en el centro (sube la corrección de errores a `H` cuando hay
  imagen central).
- **Imagen:** descarga en PNG (1200 px) y SVG.
- **Objeto 3D:** soporte de mesa (cuña a 60°, se imprime sin soportes), llavero
  (con agujero para la anilla) y placa de pared (dos agujeros para colgar).
  Texto corto en relieve opcional.
- **3MF:** dos objetos con `displaycolor` (8 dígitos hex, con byte alfa), unidad
  en milímetros, todo en el octante positivo y vértices soldados.
- **STL:** `.zip` con las dos piezas en binario + un `LEEME.txt`.
- **Avisos de calidad en vivo:** contraste WCAG entre los dos colores y tamaño en
  mm de cada módulo (por debajo de 1,5 mm la boquilla emborrona el código).

## Cómo está hecho

Sin build, sin npm en el entregable, sin frameworks. HTML + CSS + JS clásico
(patrón IIFE).

| Archivo | Qué hace |
|---|---|
| `index.html` | Página única: herramienta, SEO, FAQ, huecos de anuncios |
| `styles.css` | Hoja de estilos completa |
| `lib/manifest.js` | Configuración (`window.__BRAND__`): estilos, formatos, paletas |
| `main.js` | Diseñador del QR, descargas, avisos, publicidad |
| `qr3d.js` | Geometría del objeto, 3MF, STL y vista previa three.js |
| `server.js` | Servidor estático mínimo (solo para publicar en Railway) |

Librerías vendorizadas en `lib/vendor/` (nunca desde un CDN en producción):
`qr-code-styling` 1.9.2, `JSZip` 3.10.1 y `three` r185 (módulo + core + addons).
three.js se carga de forma **perezosa** con un mapa de importaciones e
`import()` dinámico, solo cuando la vista 3D entra en pantalla.

### Cómo se convierte un QR en relieve

1. Se lee el número de módulos real del código para calcular mm por módulo y los
   avisos de impresión.
2. Se rasteriza el **mismo** código con estilo, en blanco y negro, a ~10 px por
   módulo: esa máscara es la que genera la geometría, así lo impreso coincide
   exactamente con lo que se ve en pantalla.
3. Las celdas encendidas se fusionan en el menor número de rectángulos maximales
   (`gridRects`) y cada rectángulo se convierte en una caja, hundida 0,15 mm en
   la base para que el laminador suelde las dos piezas sin junta.

## Desarrollo

La página usa `import()` dinámico, así que **no funciona con `file://`**:

```bash
python -m http.server 8137
```

Verificación del proyecto:

```bash
python scripts/verify_project.py --project .
```

## Publicidad

Los huecos publicitarios son **placeholders vacíos** marcados con `ANUNCIO`:
banner horizontal bajo la herramienta, bloque en mitad del contenido, ventana
emergente al descargar (se abre *después* de que la descarga haya empezado, para
no bloquearla nunca) y notificación en la esquina. Busca los comentarios
`PEGA AQUÍ TU CÓDIGO DE ADSENSE` para activarlos, y añade tu gestor de
consentimiento de cookies en el `<head>`.

Las páginas legales (`privacidad.html`, `aviso-legal.html`) llevan marcas `TODO`
con los datos que hay que rellenar.

## Licencia

Código propio sin licencia pública. Las librerías de terceros conservan sus
licencias MIT originales dentro de `lib/vendor/`.

## Publicado

- Repositorio: https://github.com/JAGY2010/qr3d-generador
- Web en vivo (dominio temporal de Railway): https://lexasylum.com

El servicio de Railway esta conectado a este repositorio: **cada push a `main`
se publica solo**, sin tocar nada mas.

Cuando conectes un dominio propio, sustituye `qr3d-production.up.railway.app`
por el tuyo en `index.html` (canonical y `og:`), `privacidad.html`,
`aviso-legal.html`, `sitemap.xml` y `robots.txt`.
