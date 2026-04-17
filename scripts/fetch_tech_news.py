#!/usr/bin/env python3
"""
Tech News Aggregator - Top 50 Sources
Fetches latest tech news from curated RSS feeds and web sources.
Outputs JSON with title, summary, source, url, category, date.
"""

import json
import sys
import re
import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request
from urllib.error import URLError
from datetime import datetime, timedelta
from html import unescape
import ssl

# Disable SSL verification for some feeds
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# ===== TOP 50 SOURCES =====
RSS_FEEDS = {
    # --- US/Global Tech News ---
    "TechCrunch": "https://techcrunch.com/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
    "Wired": "https://www.wired.com/feed/rss",
    "MIT Tech Review": "https://www.technologyreview.com/feed/",
    "Hacker News": "https://hnrss.org/frontpage?count=30",
    "IEEE Spectrum": "https://spectrum.ieee.org/feeds/feed.rss",
    "404 Media": "https://www.404media.co/rss/",
    "The Information": "https://www.theinformation.com/feed",

    # --- AI/ML Specific ---
    "OpenAI Blog": "https://openai.com/blog/rss.xml",
    "Google AI Blog": "https://blog.google/technology/ai/rss/",
    "Anthropic": "https://www.anthropic.com/rss.xml",
    "Hugging Face Blog": "https://huggingface.co/blog/feed.xml",
    "DeepMind Blog": "https://deepmind.google/blog/rss.xml",
    "NVIDIA Blog": "https://blogs.nvidia.com/feed/",

    # --- Newsletters/Analysis ---
    "Stratechery": "https://stratechery.com/feed/",
    "Benedict Evans": "https://www.ben-evans.com/benedictevans?format=rss",
    "Simon Willison": "https://simonwillison.net/atom/everything",
    "Import AI": "https://importai.substack.com/feed",
    "The Batch (Andrew Ng)": "https://www.deeplearning.ai/the-batch/feed/",
    "Semafor Tech": "https://www.semafor.com/vertical/tech/rss",

    # --- Developer/Engineering ---
    "InfoQ": "https://www.infoq.com/feed/",
    "Dev.to": "https://dev.to/feed",
    "Lobsters": "https://lobste.rs/rss",
    "GitHub Blog": "https://github.blog/feed/",

    # --- Hardware/Semiconductor ---
    "SemiAnalysis": "https://semianalysis.substack.com/feed",
    "AnandTech": "https://www.anandtech.com/rss/",
    "Tom's Hardware": "https://www.tomshardware.com/feeds/all",
    "SemiWiki": "https://semiwiki.com/feed/",

    # --- China Tech (English) ---
    "Rest of World": "https://restofworld.org/feed/",
    "South China Morning Post Tech": "https://www.scmp.com/rss/4/feed",
    "TechNode": "https://technode.com/feed/",
    "Pandaily": "https://pandaily.com/feed/",

    # --- China Tech (Chinese) ---
    "36Kr": "https://36kr.com/feed",
    "虎嗅": "https://www.huxiu.com/rss/0.xml",
    "极客公园": "https://www.geekpark.net/rss",
    "机器之心": "https://www.jiqizhixin.com/rss",
    "量子位": "https://www.qbitai.com/feed",
    "品玩": "https://www.pingwest.com/feed",
    "钛媒体": "https://www.tmtpost.com/rss.xml",
    "爱范儿": "https://www.ifanr.com/feed",
    "InfoQ中文": "https://www.infoq.cn/feed",
    "少数派": "https://sspai.com/feed",

    # --- Blogs ---
    "Paul Graham": "http://www.aaronsw.com/2002/feeds/pgessays.rss",
    "Lilian Weng": "https://lilianweng.github.io/index.xml",
    "Chip Huyen": "https://huyenchip.com/feed.xml",
    "Gwern": "https://gwern.net/feed.xml",
    "Colah": "https://colah.github.io/rss.xml",
    "阮一峰": "https://www.ruanyifeng.com/blog/atom.xml",

    # --- Podcasts/Video transcripts ---
    "Latent Space": "https://www.latent.space/feed",
    "Not Boring": "https://www.notboring.co/feed",
}

def clean_html(text):
    """Remove HTML tags and clean text."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:500]

def fetch_rss(name, url, timeout=10):
    """Fetch and parse an RSS feed."""
    articles = []
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 TechAggregator/1.0'})
        with urlopen(req, timeout=timeout, context=ctx) as resp:
            data = resp.read().decode('utf-8', errors='replace')

        root = ET.fromstring(data)

        # Handle both RSS and Atom formats
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        # RSS 2.0
        items = root.findall('.//item')
        if not items:
            # Atom
            items = root.findall('.//atom:entry', ns)
            if not items:
                items = root.findall('.//{http://www.w3.org/2005/Atom}entry')

        for item in items[:10]:
            title = None
            link = None
            desc = None
            pub_date = None

            # Try RSS format
            t = item.find('title')
            if t is None:
                t = item.find('{http://www.w3.org/2005/Atom}title')
            title = t.text if t is not None and t.text else ''

            l = item.find('link')
            if l is None:
                l = item.find('{http://www.w3.org/2005/Atom}link')
                if l is not None:
                    link = l.get('href', '')
                else:
                    link = ''
            else:
                link = l.text if l.text else ''

            d = item.find('description')
            if d is None:
                d = item.find('{http://www.w3.org/2005/Atom}summary')
            if d is None:
                d = item.find('{http://www.w3.org/2005/Atom}content')
            if d is None:
                d = item.find('content:encoded', {'content': 'http://purl.org/rss/1.0/modules/content/'})
            desc = clean_html(d.text if d is not None and d.text else '')

            p = item.find('pubDate')
            if p is None:
                p = item.find('{http://www.w3.org/2005/Atom}published')
            if p is None:
                p = item.find('{http://www.w3.org/2005/Atom}updated')
            pub_date = p.text if p is not None and p.text else ''

            if title:
                articles.append({
                    'title': clean_html(title),
                    'url': link.strip() if link else '',
                    'summary': desc,
                    'source': name,
                    'date': pub_date,
                })
    except Exception as e:
        print(f"[WARN] Failed to fetch {name}: {e}", file=sys.stderr)

    return articles

def main():
    all_articles = []
    total = len(RSS_FEEDS)

    for i, (name, url) in enumerate(RSS_FEEDS.items(), 1):
        print(f"[{i}/{total}] Fetching {name}...", file=sys.stderr)
        articles = fetch_rss(name, url)
        all_articles.extend(articles)
        print(f"  -> {len(articles)} articles", file=sys.stderr)

    # Deduplicate by title similarity
    seen = set()
    unique = []
    for a in all_articles:
        key = a['title'].lower()[:60]
        if key not in seen:
            seen.add(key)
            unique.append(a)

    print(f"\nTotal: {len(unique)} unique articles from {total} sources", file=sys.stderr)
    print(json.dumps(unique, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
