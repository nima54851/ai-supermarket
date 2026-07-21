# GitHub Pages SEO Automation

Automated SEO optimization for GitHub Pages sites — OpenClaw agents maintain meta tags, sitemaps, robots.txt, and structured data automatically.

## Features
- Auto-generate `sitemap.xml` from repo structure
- Maintain `robots.txt` with proper rules
- JSON-LD structured data for articles/products
- Open Graph + Twitter Card meta tag generator
- Canonical URL management
- SEO score checker (Lighthouse-like)

## Usage
```bash
python3 seo_generator.py --repo https://github.com/nima54851/agent-studio --output _site/
```

## Files
- `seo_generator.py` — Main SEO generator
- `sitemap_builder.py` — Dynamic sitemap builder
- `meta_templates.py` — OG/Twitter card template library
- `robots_txt.py` — robots.txt manager
- `seo_checker.py` — SEO score analyzer
