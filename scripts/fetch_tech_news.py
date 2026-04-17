#!/usr/bin/env python3
"""
Tech News Aggregator - 100+ Sources (Deep & Broad)
Fetches latest tech news from curated RSS feeds covering:
- Breaking news, deep analysis, academic research, industry reports
- AI/ML, semiconductors, systems engineering, security, open source, robotics
- Chinese and global tech ecosystems
Outputs JSON with title, summary, source, url, category, date, depth_tier.
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
from concurrent.futures import ThreadPoolExecutor, as_completed

# Disable SSL verification for some feeds
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# ===== SOURCES BY DEPTH TIER =====
# tier1_deep: 深度分析、学术前沿、行业报告 (权重最高)
# tier2_quality: 高质量科技新闻、专业博客
# tier3_breadth: 广覆盖新闻、社区讨论

FEEDS = {
    # ========================================
    # TIER 1: 深度分析 & 学术前沿 (权重 x3)
    # ========================================

    # --- 顶级分析师/思想领袖 ---
    "Stratechery": ("https://stratechery.com/feed/", "tier1_deep", "analysis"),
    "Benedict Evans": ("https://www.ben-evans.com/benedictevans?format=rss", "tier1_deep", "analysis"),
    "Not Boring": ("https://www.notboring.co/feed", "tier1_deep", "analysis"),
    "Elad Gil": ("https://blog.eladgil.com/feed", "tier1_deep", "analysis"),

    # --- AI/ML 深度研究 ---
    "Lilian Weng (OpenAI)": ("https://lilianweng.github.io/index.xml", "tier1_deep", "ai_research"),
    "Chip Huyen": ("https://huyenchip.com/feed.xml", "tier1_deep", "ai_research"),
    "Colah": ("https://colah.github.io/rss.xml", "tier1_deep", "ai_research"),
    "Sebastian Raschka": ("https://magazine.sebastianraschka.com/feed", "tier1_deep", "ai_research"),
    "Jay Alammar": ("https://jalammar.github.io/feed.xml", "tier1_deep", "ai_research"),
    "The Gradient": ("https://thegradient.pub/rss/", "tier1_deep", "ai_research"),
    "Distill.pub": ("https://distill.pub/rss.xml", "tier1_deep", "ai_research"),
    "Machine Learning Mastery": ("https://machinelearningmastery.com/feed/", "tier1_deep", "ai_research"),

    # --- 半导体深度 ---
    "SemiAnalysis": ("https://semianalysis.substack.com/feed", "tier1_deep", "semiconductor"),
    "SemiWiki": ("https://semiwiki.com/feed/", "tier1_deep", "semiconductor"),
    "SemiEngineering": ("https://semiengineering.com/feed/", "tier1_deep", "semiconductor"),
    "EE Times": ("https://www.eetimes.com/feed/", "tier1_deep", "semiconductor"),
    "WikiChip": ("https://fuse.wikichip.org/feed/", "tier1_deep", "semiconductor"),

    # --- 系统/基础设施深度 ---
    "The Pragmatic Engineer": ("https://newsletter.pragmaticengineer.com/feed", "tier1_deep", "engineering"),
    "High Scalability": ("http://feeds.feedburner.com/HighScalability", "tier1_deep", "engineering"),
    "The Morning Paper": ("https://blog.acolyer.org/feed/", "tier1_deep", "engineering"),
    "Brendan Gregg": ("https://www.brendangregg.com/blog/rss.xml", "tier1_deep", "engineering"),
    "Julia Evans": ("https://jvns.ca/atom.xml", "tier1_deep", "engineering"),
    "Dan Luu": ("https://danluu.com/atom.xml", "tier1_deep", "engineering"),
    "Xe Iaso": ("https://xeiaso.net/blog.rss", "tier1_deep", "engineering"),

    # --- 安全深度 ---
    "Krebs on Security": ("https://krebsonsecurity.com/feed/", "tier1_deep", "security"),
    "Schneier on Security": ("https://www.schneier.com/feed/atom/", "tier1_deep", "security"),
    "Project Zero (Google)": ("https://googleprojectzero.blogspot.com/feeds/posts/default", "tier1_deep", "security"),
    "Trail of Bits": ("https://blog.trailofbits.com/feed/", "tier1_deep", "security"),

    # --- AI 公司官方研究博客 ---
    "OpenAI Blog": ("https://openai.com/blog/rss.xml", "tier1_deep", "ai_official"),
    "Anthropic Research": ("https://www.anthropic.com/rss.xml", "tier1_deep", "ai_official"),
    "DeepMind Blog": ("https://deepmind.google/blog/rss.xml", "tier1_deep", "ai_official"),
    "Meta AI Blog": ("https://ai.meta.com/blog/rss/", "tier1_deep", "ai_official"),
    "Microsoft Research Blog": ("https://www.microsoft.com/en-us/research/feed/", "tier1_deep", "ai_official"),
    "Apple ML Research": ("https://machinelearning.apple.com/rss.xml", "tier1_deep", "ai_official"),

    # --- 学术/论文追踪 ---
    "Papers With Code": ("https://paperswithcode.com/latest", "tier1_deep", "academic"),
    "arXiv CS.AI (recent)": ("https://rss.arxiv.org/rss/cs.AI", "tier1_deep", "academic"),
    "arXiv CS.CL (NLP)": ("https://rss.arxiv.org/rss/cs.CL", "tier1_deep", "academic"),
    "arXiv CS.LG (ML)": ("https://rss.arxiv.org/rss/cs.LG", "tier1_deep", "academic"),

    # --- Podcast 深度对谈 ---
    "Latent Space": ("https://www.latent.space/feed", "tier1_deep", "podcast"),
    "Lex Fridman": ("https://lexfridman.com/feed/podcast/", "tier1_deep", "podcast"),
    "Acquired": ("https://www.acquired.fm/episodes/feed", "tier1_deep", "podcast"),

    # ========================================
    # TIER 2: 高质量科技新闻 & 专业博客 (权重 x2)
    # ========================================

    # --- 顶级科技媒体 ---
    "MIT Tech Review": ("https://www.technologyreview.com/feed/", "tier2_quality", "news"),
    "Ars Technica": ("https://feeds.arstechnica.com/arstechnica/index", "tier2_quality", "news"),
    "IEEE Spectrum": ("https://spectrum.ieee.org/feeds/feed.rss", "tier2_quality", "news"),
    "404 Media": ("https://www.404media.co/rss/", "tier2_quality", "news"),
    "Wired": ("https://www.wired.com/feed/rss", "tier2_quality", "news"),
    "The Information": ("https://www.theinformation.com/feed", "tier2_quality", "news"),
    "Rest of World": ("https://restofworld.org/feed/", "tier2_quality", "news"),

    # --- AI/ML 生态 ---
    "Hugging Face Blog": ("https://huggingface.co/blog/feed.xml", "tier2_quality", "ai_ecosystem"),
    "NVIDIA Blog": ("https://blogs.nvidia.com/feed/", "tier2_quality", "ai_ecosystem"),
    "Google AI Blog": ("https://blog.google/technology/ai/rss/", "tier2_quality", "ai_ecosystem"),
    "Import AI": ("https://importai.substack.com/feed", "tier2_quality", "ai_ecosystem"),
    "The Batch (Andrew Ng)": ("https://www.deeplearning.ai/the-batch/feed/", "tier2_quality", "ai_ecosystem"),
    "Simon Willison": ("https://simonwillison.net/atom/everything", "tier2_quality", "ai_ecosystem"),
    "Weights & Biases Blog": ("https://wandb.ai/fully-connected/rss.xml", "tier2_quality", "ai_ecosystem"),

    # --- 云/DevOps/基础设施 ---
    "InfoQ": ("https://www.infoq.com/feed/", "tier2_quality", "devops"),
    "GitHub Blog": ("https://github.blog/feed/", "tier2_quality", "devops"),
    "Cloudflare Blog": ("https://blog.cloudflare.com/rss/", "tier2_quality", "devops"),
    "AWS Blog": ("https://aws.amazon.com/blogs/aws/feed/", "tier2_quality", "devops"),
    "Kubernetes Blog": ("https://kubernetes.io/feed.xml", "tier2_quality", "devops"),
    "Netflix Tech Blog": ("https://netflixtechblog.com/feed", "tier2_quality", "devops"),
    "Uber Engineering": ("https://eng.uber.com/feed/", "tier2_quality", "devops"),

    # --- 开源/编程语言 ---
    "Rust Blog": ("https://blog.rust-lang.org/feed.xml", "tier2_quality", "opensource"),
    "Go Blog": ("https://go.dev/blog/feed.atom", "tier2_quality", "opensource"),
    "Python Insider": ("https://blog.python.org/feeds/posts/default", "tier2_quality", "opensource"),
    "LLVM Blog": ("https://blog.llvm.org/rss.xml", "tier2_quality", "opensource"),

    # --- 个人技术博客 (有深度) ---
    "Paul Graham": ("http://www.aaronsw.com/2002/feeds/pgessays.rss", "tier2_quality", "blog"),
    "Martin Fowler": ("https://martinfowler.com/feed.atom", "tier2_quality", "blog"),
    "Joel on Software": ("https://www.joelonsoftware.com/feed/", "tier2_quality", "blog"),
    "Mitchell Hashimoto": ("https://mitchellh.com/feed.xml", "tier2_quality", "blog"),
    "Fly.io Blog": ("https://fly.io/blog/feed.xml", "tier2_quality", "blog"),

    # --- 中国科技 (深度) ---
    "机器之心": ("https://www.jiqizhixin.com/rss", "tier2_quality", "china_tech"),
    "量子位": ("https://www.qbitai.com/feed", "tier2_quality", "china_tech"),
    "InfoQ中文": ("https://www.infoq.cn/feed", "tier2_quality", "china_tech"),
    "TechNode": ("https://technode.com/feed/", "tier2_quality", "china_tech"),

    # --- 硬件/机器人 ---
    "Tom's Hardware": ("https://www.tomshardware.com/feeds/all", "tier2_quality", "hardware"),
    "IEEE Robotics": ("https://spectrum.ieee.org/feeds/topic/robotics.rss", "tier2_quality", "hardware"),

    # ========================================
    # TIER 3: 广覆盖新闻 & 社区 (权重 x1)
    # ========================================

    # --- 新闻聚合 ---
    "TechCrunch": ("https://techcrunch.com/feed/", "tier3_breadth", "news"),
    "The Verge": ("https://www.theverge.com/rss/index.xml", "tier3_breadth", "news"),
    "Hacker News (Top)": ("https://hnrss.org/frontpage?count=30", "tier3_breadth", "community"),
    "Lobsters": ("https://lobste.rs/rss", "tier3_breadth", "community"),
    "Dev.to": ("https://dev.to/feed", "tier3_breadth", "community"),
    "Semafor Tech": ("https://www.semafor.com/vertical/tech/rss", "tier3_breadth", "news"),

    # --- 中国科技新闻 ---
    "36Kr": ("https://36kr.com/feed", "tier3_breadth", "china_news"),
    "虎嗅": ("https://www.huxiu.com/rss/0.xml", "tier3_breadth", "china_news"),
    "极客公园": ("https://www.geekpark.net/rss", "tier3_breadth", "china_news"),
    "品玩": ("https://www.pingwest.com/feed", "tier3_breadth", "china_news"),
    "钛媒体": ("https://www.tmtpost.com/rss.xml", "tier3_breadth", "china_news"),
    "爱范儿": ("https://www.ifanr.com/feed", "tier3_breadth", "china_news"),
    "少数派": ("https://sspai.com/feed", "tier3_breadth", "china_news"),
    "Pandaily": ("https://pandaily.com/feed/", "tier3_breadth", "china_news"),
    "South China Morning Post Tech": ("https://www.scmp.com/rss/4/feed", "tier3_breadth", "china_news"),

    # --- 其他博客 ---
    "阮一峰": ("https://www.ruanyifeng.com/blog/atom.xml", "tier3_breadth", "blog"),
}

# Depth tier weights for scoring
TIER_WEIGHTS = {
    "tier1_deep": 3,
    "tier2_quality": 2,
    "tier3_breadth": 1,
}

def clean_html(text):
    """Remove HTML tags and clean text."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:800]  # increased from 500 for more context

def fetch_rss(name, url, tier, category, timeout=12):
    """Fetch and parse an RSS feed."""
    articles = []
    try:
        req = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 TechAggregator/2.0',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        })
        with urlopen(req, timeout=timeout, context=ctx) as resp:
            data = resp.read().decode('utf-8', errors='replace')

        root = ET.fromstring(data)

        # Handle both RSS and Atom formats
        items = root.findall('.//item')
        if not items:
            items = root.findall('.//{http://www.w3.org/2005/Atom}entry')

        for item in items[:15]:  # increased from 10
            title = None
            link = None
            desc = None
            pub_date = None

            # Title
            t = item.find('title')
            if t is None:
                t = item.find('{http://www.w3.org/2005/Atom}title')
            title = t.text if t is not None and t.text else ''

            # Link
            l = item.find('link')
            if l is None:
                l = item.find('{http://www.w3.org/2005/Atom}link')
                if l is not None:
                    link = l.get('href', '')
                else:
                    link = ''
            else:
                link = l.text if l.text else (l.get('href', '') if l.get('href') else '')

            # Description/Content (try multiple fields for richer summaries)
            for tag in ['content:encoded', 'description', '{http://www.w3.org/2005/Atom}content',
                        '{http://www.w3.org/2005/Atom}summary']:
                if tag == 'content:encoded':
                    d = item.find(tag, {'content': 'http://purl.org/rss/1.0/modules/content/'})
                else:
                    d = item.find(tag)
                if d is not None and d.text:
                    desc = clean_html(d.text)
                    break
            if not desc:
                desc = ''

            # Date
            for dtag in ['pubDate', '{http://www.w3.org/2005/Atom}published',
                         '{http://www.w3.org/2005/Atom}updated', 'dc:date']:
                p = item.find(dtag) if ':' not in dtag else item.find(dtag, {'dc': 'http://purl.org/dc/elements/1.1/'})
                if p is not None and p.text:
                    pub_date = p.text
                    break
            if not pub_date:
                pub_date = ''

            if title:
                articles.append({
                    'title': clean_html(title),
                    'url': link.strip() if link else '',
                    'summary': desc,
                    'source': name,
                    'date': pub_date,
                    'tier': tier,
                    'category': category,
                    'weight': TIER_WEIGHTS.get(tier, 1),
                })
    except Exception as e:
        print(f"[WARN] Failed to fetch {name}: {e}", file=sys.stderr)

    return articles

def main():
    all_articles = []
    total = len(FEEDS)

    # Parallel fetching for speed
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {}
        for i, (name, (url, tier, cat)) in enumerate(FEEDS.items(), 1):
            f = executor.submit(fetch_rss, name, url, tier, cat)
            futures[f] = name

        done = 0
        for f in as_completed(futures):
            done += 1
            name = futures[f]
            try:
                articles = f.result()
                all_articles.extend(articles)
                print(f"[{done}/{total}] {name}: {len(articles)} articles", file=sys.stderr)
            except Exception as e:
                print(f"[{done}/{total}] {name}: FAILED - {e}", file=sys.stderr)

    # Deduplicate by title similarity
    seen = set()
    unique = []
    for a in all_articles:
        key = re.sub(r'[^a-z0-9\u4e00-\u9fff]', '', a['title'].lower())[:50]
        if key and key not in seen:
            seen.add(key)
            unique.append(a)

    # Sort by tier weight (deep content first), then by date
    unique.sort(key=lambda x: -x['weight'])

    # Stats
    tier_counts = {}
    cat_counts = {}
    for a in unique:
        tier_counts[a['tier']] = tier_counts.get(a['tier'], 0) + 1
        cat_counts[a['category']] = cat_counts.get(a['category'], 0) + 1

    print(f"\n{'='*50}", file=sys.stderr)
    print(f"Total: {len(unique)} unique articles from {total} sources", file=sys.stderr)
    print(f"By tier: {json.dumps(tier_counts)}", file=sys.stderr)
    print(f"By category: {json.dumps(cat_counts)}", file=sys.stderr)
    print(f"{'='*50}", file=sys.stderr)

    print(json.dumps(unique, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
