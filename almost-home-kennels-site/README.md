# Almost Home Kennels website

## Deploy
Upload the contents of `dist/` to any static host (Netlify, Cloudflare Pages, Vercel) or an Apache web root.
No build step is needed to deploy.

## What's included
- 18 pages with clean URLs. Every current WordPress URL is kept (`/about/`, `/faq/`, `/new-clients/`,
  `/pricing-and-services/`, `/checklists-and-scheduling/`, `/helpful-resources/`, `/dog-boarding-in-wright-city/`
  and both blog posts), so existing Google rankings carry over.
- New SEO pages, linked from the footer: dog daycare, puppy boarding, baths & nail trims, enrichment,
  areas we serve, contact (fixes the current 404 behind "Contact Us"), and the client portal.
- `sitemap.xml` (with image entries) and `robots.txt`. Submit the sitemap in Google Search Console after launch.
- `_redirects` (Netlify/Cloudflare) and `.htaccess` (Apache) 301 old URLs such as `/home-flatsome/`,
  `/contact-us/` and the old Rank Math sitemaps.
- Every page has its own title, meta description, canonical URL, Open Graph/Twitter tags and JSON-LD
  structured data (LocalBusiness, Service with prices, FAQPage, BlogPosting, BreadcrumbList).

## Before launch
1. Add the street address to the footer and the LocalBusiness schema in `src/build.py`
   (`footer()` and `business()`). It must match the Google Business Profile exactly.
2. Add business hours if you want them in search results (`openingHoursSpecification`).
3. The client portal is a front-end preview with sample data. It has no login and saves only to the
   visitor's own browser. A real portal needs a backend (accounts, database, file storage).

## Editing
Edit `src/build.py` (pages, copy, SEO), `src/site.js` and `src/base.css`, then run `python3 src/build.py`
from this folder's parent layout (it reads images from `site/` and writes `dist/` and `preview/`).
