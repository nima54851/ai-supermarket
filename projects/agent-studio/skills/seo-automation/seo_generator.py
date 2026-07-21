#!/usr/bin/env python3
"""
GitHub Pages SEO Automation Toolkit
Generates sitemap.xml, robots.txt, Open Graph meta tags, and JSON-LD structured data.
"""
import os, json, argparse, time
from datetime import datetime

SEO_TEMPLATES = {
    "sitemap": '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>',
    "url": '  <url><loc>{loc}</loc><lastmod>{mod}</lastmod><changefreq>weekly</changefreq><priority>{pri}</priority></url>',
    "robots": "User-agent: *\nAllow: /\nSitemap: {sitemap}\n",
    "og_meta": '<meta property="og:{prop}" content="{content}">',
    "jsonld_article": '{{"@context":"https://schema.org","@type":"Article","headline":"{title}","datePublished":"{date}","author":"{{"@type":"Person","name":"{author}"}}"}}'
}

def build_sitemap(pages, base_url):
    urls = []
    for page in pages:
        urls.append(SEO_TEMPLATES["url"].format(
            loc=f"{base_url}/{page['path']}",
            mod=page.get("lastmod", datetime.now().strftime("%Y-%m-%d")),
            pri=page.get("priority", "0.8")
        ))
    return SEO_TEMPLATES["sitemap"].format(urls="\n".join(urls))

def generate_seo_package(repo_url, output_dir="_site"):
    os.makedirs(output_dir, exist_ok=True)
    base = repo_url.rstrip("/")
    
    pages = [
        {"path": "index.html", "priority": "1.0"},
        {"path": "product.html", "priority": "0.9"},
        {"path": "docs/", "priority": "0.7"},
    ]
    
    sitemap = build_sitemap(pages, base)
    with open(f"{output_dir}/sitemap.xml", "w") as f:
        f.write(sitemap)
    
    robots = SEO_TEMPLATES["robots"].format(sitemap=f"{base}/sitemap.xml")
    with open(f"{output_dir}/robots.txt", "w") as f:
        f.write(robots)
    
    print(f"✅ SEO package generated in {output_dir}/")
    print(f"   - sitemap.xml ({len(pages)} pages)")
    print(f"   - robots.txt")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--repo", default="https://nima54851.github.io/agent-studio")
    p.add_argument("--output", default="_site")
    args = p.parse_args()
    generate_seo_package(args.repo, args.output)
