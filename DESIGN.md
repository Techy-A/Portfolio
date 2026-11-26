# Design spec

The rules this site follows. Any change, by hand or by an AI tool, keeps to them. Tokens live in the `:root`
block of `src/index.template.html`; never hard-code a colour or font outside it.

## Idea

A printed title page on matte black. Times New Roman, one centre axis, and the hands from The Creation of
Adam in ASCII as the single picture. Everything else stays quiet so the hands and the evidence carry the page.

## Colour tokens

| Token | Value | Role |
|:--|:--|:--|
| `--bg` | `#0B0B0B` | matte black page, with a 7% grain overlay |
| `--surface`, `--surface-2` | `#121212`, `#181818` | jump menu and toast only |
| `--ink` | `#EDE9E2` | headings and key text (plaster white) |
| `--ink-2` | `#B3ADA3` | body text (8.8:1 on `--bg`) |
| `--ink-3` | `#8E887F` | labels and captions (5.6:1, the lowest allowed) |
| `--rule` | `#2A2826` | 1px hairlines |
| `--ochre` | `#D4B06E` | emphasis, primary button, spark. One accent. |
| `--sage` | `#9DC4AF` | what was chosen or shipped, "open to roles" dot |
| `--rose` | `#D8A3A0` | what was tested and dropped |

Every text colour passes WCAG AA (4.5:1) on `--bg`. Sage and rose always come with a mark (`[*]`, `[x]`)
so colour is never the only signal.

## Type

- `--serif` (Times New Roman, Tinos fallback) for everything people read. `--mono` (Courier Prime) only for
  ASCII, code and the `t = 0` counter.
- One size per level: h1 `clamp(54px, 10vw, 116px)`, h2 `clamp(32px, 4.4vw, 48px)`, h3 `26px`, body `19px`,
  labels `15 to 16px` small capitals with `.12 to .24em` tracking. Figures (`.readout .n`) stay under the h2 size.
- Body line height 1.6. Paragraphs at most 66 characters wide.
- Short lines (labels, headings, one-line paragraphs) are centred. Paragraphs longer than two lines sit in a
  centred column with one left edge.

## Layout

- One container (`.wrap`, max 1180px) and one book column (66ch) on the centre axis.
- Sections are separated by a 1px `--rule` and 56px / 80px vertical padding.
- Phone: everything stacks to one column, tap targets at least 44px tall, no horizontal scroll at 320px.

## Actions

- One primary action, **Resume (PDF)**, drawn the same everywhere: the hero, the closing section and a smaller
  copy in the nav. One secondary, **Email me**, outlined. LinkedIn and GitHub are text links under them.
- At most two buttons in the hero and two in the closing section.

## Motion

- Transitions 150 to 300ms, `ease-out`. Animate `transform`, `opacity` and colour only.
- Buttons lift 2px on hover (pointer devices only) and press to `scale(.98)`.
- One orchestrated moment: the hands denoise from noise in 40 steps on load. Nothing else animates on load.
- `prefers-reduced-motion: reduce` turns every transition and animation off; the finished image shows at once.

## Copy

- No em dashes, no en dashes, no emoji. Every text file is plain 7-bit ASCII.
- Plain verbs, sentence case, numbers from the real projects only. No ranks or scores from private competitions.
