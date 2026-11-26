# Design spec

The rules this site follows. Any change, by hand or by an AI tool, keeps to them. Tokens live in the `:root`
block of `src/index.template.html`; never hard-code a colour, font or easing outside it.

## Idea

A cinematic opening: the hands from The Creation of Adam in ASCII, big and centred, with the name under the
gap between the fingertips. Below it, editorial split sections: a sticky label column on the left, content on
the right, separated by hairlines. No cards, no boxes, no gradients.

## Bans

1. No purple or indigo gradients, no default blue accents, no pure `#000` or `#FFF` surfaces.
2. Two type families plus one mono for code: Clash Display (name, headings), Bricolage Grotesque (text), Space Mono (labels, figures, ASCII). Never Inter.
3. No three-column icon-in-a-box feature grids, no glassmorphism panels. Hairlines and type do the work.
4. No emoji, no em dashes, no en dashes. Every text file is plain 7-bit ASCII.
5. No title case: sentence case for headings, buttons and labels. Uppercase only for small mono labels.
6. No fake metrics or social proof. Every number comes from a real project.
7. No scroll-triggered fades on text. Motion is for feedback only.

## Colour (OKLCH)

Neutrals carry a faint cool tint; the accent is the only saturated colour.

| Token | Charcoal (default) | Warm stone (light) | Role |
|:--|:--|:--|:--|
| `--bg` | `oklch(0.155 0.006 260)` | `oklch(0.982 0.004 85)` | page |
| `--ink` | `oklch(0.93 0.008 85)` | `oklch(0.2 0.008 260)` | headings, key text |
| `--ink-2` | `oklch(0.76 0.01 85)` | `oklch(0.42 0.008 85)` | body text |
| `--ink-3` | `oklch(0.63 0.012 85)` | `oklch(0.52 0.01 85)` | labels, captions |
| `--rule` | ink at 10% | ink at 12% | hairlines |
| `--accent` | `oklch(0.79 0.1 80)` gold | `oklch(0.5 0.1 70)` deep gold | the one accent |
| `--sage` / `--rose` | chosen / dropped | chosen / dropped | always with `[*]` or `[x]` |

Measured contrast on `--bg`: lowest is `--ink-3` at 5.6:1 (charcoal) and 5.2:1 (stone). Hover states mix the
accent with `color-mix(in oklch, ...)` instead of new hex values.

## Themes

`data-theme` on `<html>`: `dark` or `light`. First visit follows the system setting; the nav button (and the
jump menu's "Switch theme") flips it and remembers the choice in `localStorage`. The ASCII hands are recoloured
from `--ink` on a canvas, so they work on both.

## Type

- Clash Display (self-hosted in `fonts/`, 500 and 600) for the name, headings and project titles.
- Bricolage Grotesque (variable) for body text. Space Mono for labels, figures, the tagline and ASCII.
- h1 `clamp(52px, 10vw, 132px)`, tracking `-0.025em`; h2 `clamp(32px, 4.6vw, 56px)`, `-0.035em`; h3 24 to 36px.
  Body 18px / 1.6, paragraphs at most 64 characters wide.
- Dark theme uses weight 500 for display text, light uses 600, so strokes look equally thick.
- Mono labels: 11 to 12px, uppercase, `+0.08em` tracking. Figures use `tabular-nums`.
- `text-wrap: balance` on headings, `pretty` on paragraphs.

## Layout

- One container, max 1200px, 40px gutters on desktop and 20px on phones.
- Sections: a 240px sticky label column and a content column, 1px hairline between sections.
- Phone: one column, tap targets 40 to 44px, small controls get an invisible 8px hit area, no sideways scroll at 320px.

## Actions

- One primary action, **Resume (PDF)**: gold pill in the nav, the hero and the closing section.
- One secondary, **Email me**, outlined. LinkedIn and GitHub are text links.

## Motion

- 150 to 250ms, easing `cubic-bezier(.22, 1, .36, 1)`. Animate `transform`, `opacity` and colour only.
- Buttons lift 2px on hover and press to `scale(.97)`. Project rows slide 10px on hover.
- One orchestrated moment: the hands denoise from noise in 40 steps on load.
- A 2px reading-progress bar driven by a CSS scroll timeline (no JavaScript).
- The sticky header uses a layered progressive blur instead of a hard edge.
- `prefers-reduced-motion: reduce` turns every transition and animation off.
