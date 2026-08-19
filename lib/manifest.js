(function () {
  "use strict";

  /* Datos de marca y configuracion de la herramienta.
     El CONTENIDO editorial (textos, FAQ, pasos) vive en el HTML: esto es solo
     configuracion que el JS necesita. Unico global: window.__BRAND__ */

  window.__BRAND__ = {
    name: "QR3D",
    tagline: "Generador de codigos QR para imprimir en 3D",

    /* Un unico control de estilo -> las tres opciones internas a la vez */
    styles: {
      clasico:    { dots: "square",         corners: "square",        cornerDot: "square" },
      redondeado: { dots: "rounded",        corners: "extra-rounded", cornerDot: "dot"    },
      puntos:     { dots: "dots",           corners: "dot",           cornerDot: "dot"    },
      elegante:   { dots: "classy-rounded", corners: "extra-rounded", cornerDot: "square" }
    },

    /* Emojis para el centro del codigo */
    emojis: ["\uD83C\uDF7D\uFE0F", "\u2B50", "\uD83D\uDCF6", "\uD83D\uDCCD", "\uD83D\uDCF7",
             "\uD83C\uDFB5", "\uD83D\uDECD\uFE0F", "\uD83C\uDF89", "\u2764\uFE0F", "\uD83D\uDC4D",
             "\uD83C\uDFE0", "\uD83D\uDCAC", "\uD83C\uDF7A", "\u2615", "\uD83D\uDD11", "\uD83D\uDE80"],

    /* Paletas rapidas: [color del codigo, color del fondo/base] */
    palettes: [
      ["#141821", "#f4f2ec"],
      ["#0f2f5f", "#e8f0fb"],
      ["#8a2c1b", "#f6ece2"],
      ["#14432f", "#e9f3ea"],
      ["#2b2140", "#efe9f7"],
      ["#101010", "#ffd400"]
    ],

    /* Formatos de objeto 3D (medidas en milimetros) */
    formats: {
      soporte: {
        label: "Soporte de mesa",
        defaultSize: 78, min: 55, max: 130,
        angle: 60,          /* grados sobre la horizontal */
        lip: 2.6,           /* labio frontal, evita el filo */
        topBand: 0,
        hint: "Se imprime sin soportes: la cara del codigo mira hacia arriba."
      },
      llavero: {
        label: "Llavero",
        defaultSize: 48, min: 35, max: 80,
        thickness: 3,
        topBand: 11,
        ringR: 2.6,
        hint: "Placa fina con agujero para la anilla."
      },
      placa: {
        label: "Placa de pared",
        defaultSize: 95, min: 60, max: 160,
        thickness: 3.2,
        topBand: 11,
        holeR: 2.3,
        hint: "Dos agujeros arriba para colgarla con tornillos o cinta."
      }
    },

    /* Reglas de calidad de impresion */
    print: {
      minModuleMm: 1.5,     /* por debajo, la boquilla redondea el codigo */
      minContrast: 3,       /* ratio WCAG minimo para que el movil lo lea */
      reliefDefault: 1.2,
      reliefMin: 0.8,
      reliefMax: 2.0
    }
  };
})();
