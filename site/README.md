# Landing page

The website for Open Finance Toolkit. It is a small React + Vite project and is **not** part of the PyPI package.

It is published at https://itz-https.github.io/open-finance-toolkit/ by the "Deploy landing page" workflow every time something under `site/` changes on `main`.

## One-time setup

1. In the repository, open **Settings**, then **Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Merge to `main` (or run the "Deploy landing page" workflow by hand from the **Actions** tab).

## Common edits

| To change | Edit |
|---|---|
| The live dashboard link, repository link, install command | `src/config.js` (set `DEMO_URL` once your Streamlit app is live) |
| Text, features, supported banks, contribution cards | `src/App.jsx` (the lists at the top of the file) |
| Colours, spacing, fonts | `src/styles.css` (colours are at the top, in `:root`) |

## Run it on a computer

```bash
cd site
npm install
npm run dev      # live preview
npm run build    # production build into site/dist
```

## Third-party code

The animated components in `src/reactbits/` come from [React Bits](https://reactbits.dev) by David Haz, used under its "MIT + Commons Clause" licence (see `src/reactbits/LICENSE.md`). They may be used inside a website or application like this one. They may not be sold or redistributed as components on their own, so please do not copy that folder into a component library or template pack.
