# Quiet Leverages website

Static storefront for Quiet Leverages: a home page and one conversion landing page for each of the 25 Gumroad products. Buy buttons link out to Gumroad checkout, so the site handles no payments.

```
site/        deployable static site (index.html, one HTML page per product, site.css, site.js, reviews.json, img/)
generator/   Python that builds site/ from one JSON file per product
```

## Rebuild the site

```
python3 generator/build_site.py
```

Python 3 only, no dependencies. It reads `generator/data/*.json` and `generator/img/`, and rewrites everything in `site/`. Do not edit the HTML in `site/` by hand; change the JSON or the generator and rebuild.

## Common edits

- **Copy for one product:** edit `generator/data/<slug>.json`, rebuild.
- **Gumroad store URL:** change `STORE` at the top of `generator/build.py`. The store subdomain is still unconfirmed, so every buy button currently points at `https://quietleverages.gumroad.com/l/<slug>`.
- **Page layout and styles:** `generator/build_site.py` (`EXTRA_CSS`, `product_page`, `index_page`) and the base `CSS` in `generator/build.py`.
- **Product list, order and one-line summaries:** `SUMMARY`, `FREE`, `KITS`, `FLAG` in `generator/build_site.py`.

## Social proof

Pages show only proof that exists: sourced statistics, real pages from each product, and true price comparisons. Reader reviews and star ratings are built in but hidden. Add real reviews (for example copied from Gumroad) to `site/reviews.json`, and the matching product page shows them:

```json
{ "items": [ { "slug": "raise-kit", "name": "First name", "rating": 5, "text": "Review text.", "source": "Gumroad" } ] }
```

`reviews.json` is kept across rebuilds, so adding reviews is safe. Never add invented reviews.

## Checkout

Buy buttons open Gumroad's overlay checkout on the page (Gumroad's `gumroad.js` plus its `data-gumroad-overlay-checkout` attribute). If that script fails to load, the button is a normal link to `https://quietleverages.gumroad.com/l/<slug>`. Products must be **Published** in Gumroad before checkout works for buyers. The look of the checkout window itself is set in Gumroad (profile and product settings), not in this repo.

## Motion

Scroll reveals, count-up numbers, hero entrance, cover tilt, a scroll progress bar and button and card hover effects live in `site/site.js` and the `/* motion */` block of `EXTRA_CSS`. All timings are 200-700ms. Everything is switched off under `prefers-reduced-motion`, and pages are fully visible without JavaScript.

## Hosting (GitHub Pages + GoDaddy domain)

`.github/workflows/pages.yml` deploys `site/` to GitHub Pages on every push to `main`. Repo: `github.com/quietleverages/website`. `site/CNAME` holds `quietleverages.com`.

1. Repo Settings > Pages > Source: **GitHub Actions**. Custom domain: `quietleverages.com`. Tick **Enforce HTTPS** once the certificate is ready.
2. GoDaddy DNS for `quietleverages.com`: delete the default parked `A` record, then add four `A` records for `@` pointing to `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`, and a `CNAME` for `www` pointing to `quietleverages.github.io`.
3. Wait for DNS to spread (minutes to a few hours). Free GitHub Pages needs a public repo.

`site/` also carries `404.html`, `robots.txt` and `sitemap.xml`, all generated.

## Brand rules

Voice, banned words, the stat bank and the facts rule live in `CLAUDE.md` in the Quiet Leverages working folder. Page copy follows them.
