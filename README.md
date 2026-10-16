# casanovanjpa.com

Static site for Nicholas Rodriguez Jr. / Casanova Group, built to be hosted on GitHub Pages.

- `src/pages/` holds each page's content. `tools/build.py` wraps them in the shared header, footer and SEO tags.
- `static/` holds the CSS, JavaScript, images, icons, `CNAME`, `robots.txt` and the web manifest.
- Run `python3 tools/build.py`. It writes `docs/`, which is what GitHub Pages serves (Settings → Pages → Deploy from branch → `main` / `/docs`), and `preview/`, which you can open straight from disk.

## Settings in `static/assets/js/site.js`
- `gaId`: Google Analytics ID (kept from the Soloist site). It loads only after a visitor accepts cookies.
- `formspreeId`: paste a free Formspree form ID to have the contact form email you. While it is empty, the form opens the visitor's email app instead.

## DNS for GitHub Pages
- Four A records on `casanovanjpa.com`: 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153
- CNAME `www` → `casanovaforsale-ctrl.github.io`
- Leave the `app.casanovanjpa.com` record alone: the Open House app runs there on Fly.io.
