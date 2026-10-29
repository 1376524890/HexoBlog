# Hexo blog workspace

- Source branch: `master`.
- Generated site branch: `static-site`; publish only `public/` through GitHub Actions.
- Blog source and assets: `source/`.
- Novel manuscript and catalog: `novels/tingcheng/`; keep all 51 chapters numbered 0–50.
- Novel generator: `scripts/novels.js`.
- Install dependencies with `npm ci`; build with `npm run build`.
- Validate novel output with `npm run verify:novel`.
- Do not commit `node_modules/`, `public/`, `db.json`, credentials, or local environments.
- Do not push or change production deployment settings unless the user authorizes it.
