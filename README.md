# Portfolio

Personal portfolio of Aryan Awasthi: machine learning, model evaluation and data.

```
      .o.       ooooooooo.   oooooo   oooo       .o.       ooooo      ooo
     .888.      `888   `Y88.  `888.   .8'       .888.      `888b.     `8'
    .8"888.      888   .d88'   `888. .8'       .8"888.      8 `88b.    8
   .8' `888.     888ooo88P'     `888.8'       .8' `888.     8   `88b.  8
  .88ooo8888.    888`88b.        `888'       .88ooo8888.    8     `88b.8
 .8'     `888.   888  `88b.       888       .8'     `888.   8       `888
o88o     o8888o o888o  o888o     o888o     o88o     o8888o o8o        `8
```

A single static page with no framework and no build step at runtime.

## Files

| Path | What it is |
|:--|:--|
| `index.html` | The site. Open it in a browser, or serve the repo root with GitHub Pages. |
| `src/index.template.html` | Source for `index.html`, with placeholders for the ASCII hands. |
| `src/fresco.py` | Renders the hands from a public-domain scan of The Creation of Adam as tonal ASCII. Writes `src/fresco.json`. |
| `src/build.py` | Puts the hands, their colours and the spark into the template and writes `index.html`. |
| `src/og.py`, `src/og.html` | Source for `og.png`, the 1200 x 627 link preview. Screenshot `og.html` at that size to regenerate. |
| `llms.txt` | Plain-text summary of the page for AI assistants. |
| `AryanAwasthi.pdf` | Resume, linked from the page. |

## Editing

Change copy and styles in `src/index.template.html`, then rebuild:

```bash
python src/build.py
```

To re-render the hands (only needed if the rendering changes):

```bash
pip install numpy scipy pillow
curl -L -o adam.jpg "https://upload.wikimedia.org/wikipedia/commons/5/5b/Michelangelo_-_Creation_of_Adam_%28cropped%29.jpg"
python src/fresco.py adam.jpg && python src/og.py && python src/build.py
```

## Design notes

- Matte black with a fine grain. Three muted accents carry meaning: ochre for emphasis and the spark, sage for what was chosen or shipped, rose for what was tested and dropped.
- Human and machine: Cormorant Garamond (a Renaissance face) for display, Geist for text, Geist Mono for labels and ASCII, Doto (dot matrix) only for metric readouts.
- The hands come from a public-domain scan of the fresco, with a short stretch of each forearm. Skin is told apart from the plaster by saturation plus darkness, keeping only regions with a clearly skin-coloured core, so stains in the plaster drop out. Adam's fingers overlap in shadow, so the seams between them are traced by hand on the fresco (`SEAMS` in `src/fresco.py`) and cut as clean one-character channels, together with the plaster seen between his fingers. Skin keeps a minimum character density and each character is coloured by the light on it, from deep ochre to plaster white, so shaded fingers stay solid. Phones get a tighter crop on the fingertips. The arm ends dissolve into fine dust, and a glowing spark sits in the gap between the fingertips.
- On load the hands are denoised from random characters in 40 steps, like a diffusion sampler. "Sample again" reruns it. Reduced motion shows the finished image.
- Ctrl K, Cmd K or / opens a jump menu: sections, resume, copy email, GitHub, LinkedIn.
- The first screen holds what a recruiter scans for: name, headline, resume button and a model card (role sought, latest role and dates, education, location, stack, contact).
- House style: no em dashes, no en dashes, no emoji. Every file is plain 7-bit ASCII.

## Publishing

`SITE` in `src/build.py` is the public address used for the link preview and search metadata. It defaults to `https://techy-a.github.io/portfolio/`; change it and rebuild if the site lives elsewhere.


Settings, Pages, deploy from branch `main`, folder `/ (root)`. Pages on a private repository needs a paid GitHub plan; on a free plan, make the repository public first.
