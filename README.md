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
| `src/index.template.html` | Source for `index.html`, with placeholders for the ASCII name lettering. |
| `src/build.py` | Renders the FIGlet lettering into the template and writes `index.html`. |
| `AryanAwasthi.pdf` | Resume, linked from the page. |

## Editing

Change copy and styles in `src/index.template.html`, then rebuild:

```bash
pip install pyfiglet
python src/build.py
```

## Design notes

- Type: Schibsted Grotesk for prose, Martian Mono for labels and ASCII figures, Doto (dot matrix) only for metric readouts.
- Lettering: FIGlet Roman on desktop, Small Slant on phones. The name resolves out of noise on load and stays still when reduced motion is on.
- Every ASCII figure carries real content: the error Whisper corrects away, the leaderboard history, each project's pipeline and the timeline.
- House style: no em dashes, no en dashes, no emoji. The source is plain 7-bit ASCII.

## Publishing

Settings, Pages, deploy from branch `main`, folder `/ (root)`. Pages on a private repository needs a paid GitHub plan; on a free plan, make the repository public first.
