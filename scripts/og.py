#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera assets/img/og-cover.png (1200x630), la tarjeta social del sitio.
Dev-only: no se despliega. Ejecutar desde la raiz del proyecto."""
import os
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
DEEP = (21, 27, 43)
CREAM = (244, 242, 236)
ACCENT = (255, 90, 31)
MUTE = (154, 163, 181)


def font(size, bold=True):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


img = Image.new("RGB", (W, H), DEEP)
d = ImageDraw.Draw(img)

# franja de acento
d.rectangle([0, 0, 14, H], fill=ACCENT)

# QR decorativo a la derecha (determinista)
random.seed(7)
qx, qy, cell = 760, 150, 22
n = 15
for r in range(n):
    for c in range(n):
        in_eye = (r < 4 and c < 4) or (r < 4 and c >= n - 4) or (r >= n - 4 and c < 4)
        if in_eye:
            continue
        if random.random() < 0.52:
            d.rounded_rectangle(
                [qx + c * cell, qy + r * cell, qx + c * cell + cell - 3, qy + r * cell + cell - 3],
                radius=4, fill=CREAM)


def eye(ox, oy):
    d.rounded_rectangle([ox, oy, ox + cell * 4 - 3, oy + cell * 4 - 3], radius=10, fill=ACCENT)
    d.rounded_rectangle([ox + cell, oy + cell, ox + cell * 3 - 3, oy + cell * 3 - 3], radius=6, fill=DEEP)
    d.rounded_rectangle([ox + cell * 1.5, oy + cell * 1.5, ox + cell * 2.5 - 3, oy + cell * 2.5 - 3],
                        radius=4, fill=CREAM)


eye(qx, qy)
eye(qx + cell * (n - 4), qy)
eye(qx, qy + cell * (n - 4))

# sombra/base 3D bajo el QR
d.polygon([(qx - 26, qy + cell * n + 16), (qx + cell * n + 26, qy + cell * n + 16),
           (qx + cell * n + 60, qy + cell * n + 62), (qx - 60, qy + cell * n + 62)], fill=(31, 39, 60))

# texto
d.text((72, 132), "GRATIS  ·  SIN REGISTRO  ·  3MF A DOS COLORES", font=font(21), fill=ACCENT)
d.text((72, 186), "Codigo QR", font=font(70), fill=CREAM)
d.text((72, 262), "para imprimir", font=font(70), fill=CREAM)
d.text((72, 338), "en 3D", font=font(70), fill=ACCENT)
d.text((72, 448), "Soporte de mesa · Llavero · Placa de pared", font=font(26, False), fill=MUTE)
d.text((72, 486), "PNG · SVG · 3MF · STL", font=font(26, False), fill=MUTE)
d.text((72, 552), "QR3D", font=font(30), fill=CREAM)

os.makedirs("assets/img", exist_ok=True)
img.save("assets/img/og-cover.png", optimize=True)
print("assets/img/og-cover.png", os.path.getsize("assets/img/og-cover.png"), "bytes")
