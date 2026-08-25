# jackwetherell.github.io

Personal site of Dr. Jack Wetherell, served by GitHub Pages from the repository
root. Static HTML with no dependencies: no npm, no Jekyll, no build toolchain
beyond Python 3, which every machine already has.

## How it fits together

```
templates/base.html   page shell: <head>, header, nav, footer
content/<slug>.html   the body of one page (this is what you edit)
build.py              stitches the two together into <slug>.html at the root
assets/css/site.css   all styling
assets/js/site.js     mobile nav toggle (the site works without it)
images/, files/       photos, figures, PDFs
```

Pages at the repository root (`index.html`, `research.html`, …) plus
`sitemap.xml` are **generated**. Do not edit them by hand — edit
`content/` or `templates/` and rebuild.

## Editing the site

1. Edit the relevant file in `content/`, or `templates/base.html` for anything
   that appears on every page.
2. Rebuild:

   ```sh
   python3 build.py
   ```

3. Preview locally:

   ```sh
   python3 -m http.server 8000     # then open http://localhost:8000
   ```

4. Commit both the `content/` change and the regenerated pages.

`python3 build.py --check` reports whether the committed pages match the
content without writing anything; GitHub Actions runs it on every push.

## Adding a page

Add an entry to the `PAGES` list in `build.py` (slug, nav label, title, meta
description), create `content/<slug>.html`, and rebuild. The navigation,
`sitemap.xml`, and the "current page" highlight all follow automatically.
Set `"nav": None` for a page that should exist but not appear in the menu.

## Conventions

- Content files are HTML fragments — no `<html>`, `<head>` or `<body>`.
- Useful classes: `panel` (card surface), `section` + `wrap` (page section),
  `prose` (readable line length), `entry-list`/`entry` (publications and
  patents), `plain-list`, `card-grid`, `video` (responsive 16:9 embed),
  `figure-side` (figure floated beside text on wide screens).
- Every `<img>` needs `alt`, plus `width`/`height` so the page does not shift
  while loading. Use `loading="lazy"` for anything below the fold.
- Resize photographs before committing them; nothing needs to be wider than
  about 1600px.
