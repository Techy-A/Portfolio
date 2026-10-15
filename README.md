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
| `src/index.template.html` | Source for `index.html`. |
| `src/build.py` | Fills in the site address and writes `index.html`. |
| `adam.jpg` | The ASCII rendering of the hands from The Creation of Adam shown below the introduction. |
| `src/og.py`, `src/og.html` | Source for `og.png`, the 1200 x 627 link preview. Screenshot `og.html` at that size to regenerate. |
| `llms.txt` | Plain-text summary of the page for AI assistants. |
| `AryanAwasthi.pdf` | Resume, linked from the page. |

## Editing

Change copy and styles in `src/index.template.html`, then rebuild:

```bash
python src/build.py
```

To redo the link preview after a change, run `python src/og.py` and screenshot `src/og.html` at 1200 x 627 as `og.png`.

## Design notes

- Matte black with a fine grain. Three muted accents carry meaning: ochre for emphasis and the spark, sage for what was chosen or shipped, rose for what was tested and dropped.
- Set entirely in Times New Roman (Tinos as the fallback where it is not installed), with small capitals for labels and italics for asides. Courier Prime, its typewriter partner, sets the ASCII. Every heading, label and short paragraph sits on one centre axis, like a printed title page.
- The hands are `adam.jpg`, an ASCII rendering of the hands from The Creation of Adam. A canvas turns its black into transparency, so the characters sit directly on the page's matte black and grain, and the forearms fade out at the left and right edges. Phones get a tighter crop on the two hands and the gap between them. A glowing spark sits in the gap between the fingertips.
- On load the picture is denoised from random noise in 40 steps, like a diffusion sampler. "Sample again" reruns it. Reduced motion shows the finished image, and if the canvas is unavailable the plain image is shown.
- Ctrl K, Cmd K or / opens a jump menu: sections, resume, copy email, GitHub, LinkedIn.
- The first screen is a centred title page with what a recruiter scans for: name, headline, resume, email, LinkedIn and GitHub, and an at-a-glance table (role sought, latest role and dates, education, location, stack, contact).
- House style: no em dashes, no en dashes, no emoji. Every text file is plain 7-bit ASCII.

## Publishing

`SITE` in `src/build.py` is the public address used for the link preview and search metadata. It defaults to `https://techy-a.github.io/portfolio/`; change it and rebuild if the site lives elsewhere.


Settings, Pages, deploy from branch `main`, folder `/ (root)`. Pages on a private repository needs a paid GitHub plan; on a free plan, make the repository public first.
