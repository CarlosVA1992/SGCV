# Identidad visual — Huellitas

## Paleta de colores

| Uso | Color | Hex |
|-----|-------|-----|
| Primario (marca) | Verde veterinario | `#2E7D6B` |
| Primario oscuro | Verde profundo | `#1F5A4D` |
| Acento | Naranja cálido | `#F2A65A` |
| Fondo | Blanco humo | `#F7F7F5` |
| Texto principal | Gris carbón | `#2B2B2B` |
| Texto secundario | Gris medio | `#6B6B6B` |
| Borde | Gris claro | `#E0E0E0` |

## Colores por estado de cita

| Estado | Color | Hex |
|--------|-------|-----|
| Programada | Azul | `#3B82F6` |
| En atención | Amarillo | `#F59E0B` |
| Reprogramada | Morado | `#8B5CF6` |
| Cancelada | Rojo | `#EF4444` |
| Inasistencia | Gris | `#6B7280` |

## Tipografía

- **Títulos:** `Nunito`, sans-serif, 600/700
- **Cuerpo:** `Inter`, sans-serif, 400/500
- Fallback: `system-ui, -apple-system, sans-serif`

## Logo

- Simple: huella de pata + texto "Huellitas"
- Se entrega como SVG en `web/static/img/logo.svg`
- Fondo transparente, funciona en claro y oscuro

## Componentes base

- Botón primario: fondo `#2E7D6B`, texto blanco, borde redondeado 6px
- Botón secundario: borde `#2E7D6B`, texto `#2E7D6B`, fondo transparente
- Card: fondo blanco, borde `#E0E0E0`, sombra suave, radio 8px
- Input: borde `#E0E0E0`, radio 6px, foco con borde `#2E7D6B`

## Principios

1. Consistencia: todas las pantallas usan `base.html`.
2. Claridad: colores de estado distinguibles.
3. Simplicidad: sin decoración innecesaria.
4. Accesibilidad: contraste mínimo AA.