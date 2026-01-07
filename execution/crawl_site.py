import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import sys
from typing import Dict, List, Set, Optional

def safe_get(url: str, timeout: int = 5) -> Optional[str]:
    """Safely fetch URL content with error handling."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; MojoAEOChecker/1.0)'}
        response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}", file=sys.stderr)
    return None

def fetch_sitemap(domain: str) -> List[str]:
    """Fetch and parse sitemap.xml to get list of URLs."""
    sitemap_url = f"{domain}/sitemap.xml"
    content = safe_get(sitemap_url)
    
    urls = []
    if content:
        try:
            soup = BeautifulSoup(content, 'xml')
            # Handle sitemap index (points to other sitemaps)
            sitemap_tags = soup.find_all('sitemap')
            if sitemap_tags:
                for sitemap in sitemap_tags[:5]:  # Limit to 5 sub-sitemaps
                    loc = sitemap.find('loc')
                    if loc:
                        sub_content = safe_get(loc.text)
                        if sub_content:
                            sub_soup = BeautifulSoup(sub_content, 'xml')
                            for url_tag in sub_soup.find_all('url'):
                                loc_tag = url_tag.find('loc')
                                if loc_tag:
                                    urls.append(loc_tag.text)
            else:
                # Regular sitemap
                for url_tag in soup.find_all('url'):
                    loc = url_tag.find('loc')
                    if loc:
                        urls.append(loc.text)
        except Exception as e:
            print(f"Error parsing sitemap: {str(e)}", file=sys.stderr)
    
    return urls[:50]  # Limit to 50 URLs

def extract_page_data(url: str, html: str) -> Dict:
    """Extract relevant data from a page."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract title
    title_tag = soup.find('title')
    title = title_tag.text.strip() if title_tag else ""
    
    # Extract meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    description = meta_desc.get('content', '').strip() if meta_desc else ""
    
    # Extract headings
    h1_tags = [h.text.strip() for h in soup.find_all('h1')]
    h2_tags = [h.text.strip() for h in soup.find_all('h2')]
    
    # Extract links
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.text.strip()
        if text and href:
            links.append({'text': text, 'href': href})
    
    # Check for Schema.org markup
    schema_types = []
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and '@type' in data:
                schema_types.append(data['@type'])
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and '@type' in item:
                        schema_types.append(item['@type'])
        except:
            pass
    
    # Extract main content (first few paragraphs)
    paragraphs = [p.text.strip() for p in soup.find_all('p') if len(p.text.strip()) > 50]
    main_content = ' '.join(paragraphs[:3])[:500] if paragraphs else ""
    
    return {
        'url': url,
        'title': title,
        'description': description,
        'h1': h1_tags,
        'h2': h2_tags,
        'links': links[:20],  # Limit links
        'schema_types': schema_types,
        'content_preview': main_content
    }

def categorize_page(page_data: Dict) -> str:
    """Categorize a page based on its URL and content."""
    url = page_data['url'].lower()
    title = page_data['title'].lower()
    
    # Check URL patterns
    if any(x in url for x in ['/about', '/company', '/who-we-are']):
        return 'About'
    elif any(x in url for x in ['/product', '/service', '/solution']):
        return 'Products'
    elif any(x in url for x in ['/doc', '/guide', '/tutorial', '/help']):
        return 'Documentation'
    elif any(x in url for x in ['/blog', '/news', '/article']):
        return 'Blog'
    elif any(x in url for x in ['/contact', '/support']):
        return 'Contact'
    elif any(x in url for x in ['/pricing', '/plan']):
        return 'Pricing'
    
    # Check title patterns
    if any(x in title for x in ['about', 'company', 'who we are']):
        return 'About'
    elif any(x in title for x in ['product', 'service', 'solution']):
        return 'Products'
    elif any(x in title for x in ['documentation', 'guide', 'tutorial']):
        return 'Documentation'
    
    return 'Other'

def analyze_site_structure(pages: List[Dict]) -> Dict:
    """Analyze crawled pages to understand site structure."""
    categories = {}
    all_schema_types = set()
    
    for page in pages:
        category = categorize_page(page)
        if category not in categories:
            categories[category] = []
        categories[category].append(page)
        all_schema_types.update(page['schema_types'])
    
    # Find homepage
    homepage = next((p for p in pages if urlparse(p['url']).path in ['/', '']), pages[0] if pages else None)
    
    return {
        'categories': categories,
        'schema_types': list(all_schema_types),
        'homepage': homepage,
        'total_pages': len(pages)
    }

def generate_llm_txt(domain: str, analysis: Dict) -> str:
    """Generate optimized llm.txt file based on site analysis."""
    homepage = analysis['homepage']
    categories = analysis['categories']
    
    # Extract company name from homepage title or domain
    company_name = homepage['title'].split('|')[0].strip() if homepage and homepage['title'] else urlparse(domain).netloc
    
    # Get description from homepage meta or first paragraph
    description = homepage['description'] if homepage and homepage['description'] else \
                  homepage['content_preview'][:200] if homepage and homepage['content_preview'] else \
                  f"Information and resources from {company_name}"
    
    # Build llm.txt content
    lines = [
        f"# {company_name}",
        "",
        f"> {description}",
        ""
    ]
    
    # Add sections for each category
    priority_categories = ['About', 'Products', 'Documentation', 'Pricing', 'Contact']
    other_categories = [c for c in categories.keys() if c not in priority_categories and c != 'Other']
    
    for category in priority_categories + other_categories:
        if category in categories and categories[category]:
            lines.append(f"## {category}")
            for page in categories[category][:5]:  # Top 5 pages per category
                title = page['title'] or page['h1'][0] if page['h1'] else 'Page'
                # Make URL relative if same domain
                url = page['url']
                if url.startswith(domain):
                    url = url[len(domain):]
                desc = page['description'][:100] if page['description'] else ""
                if desc:
                    lines.append(f"- [{title}]({url}): {desc}")
                else:
                    lines.append(f"- [{title}]({url})")
            lines.append("")
    
    # Add optional section for blog/news if exists
    if 'Blog' in categories:
        lines.append("## Optional")
        for page in categories['Blog'][:3]:
            title = page['title'] or 'Blog Post'
            url = page['url']
            if url.startswith(domain):
                url = url[len(domain):]
            lines.append(f"- [{title}]({url})")
        lines.append("")
    
    return '\n'.join(lines)

def generate_ai_txt(domain: str, analysis: Dict) -> str:
    """Generate optimized ai.txt file with agent instructions."""
    homepage = analysis['homepage']
    categories = analysis['categories']
    
    lines = [
        "# AI Agent Directives",
        "User-agent: *",
        "Allow: /",
        "",
        "# Agent-specific instructions"
    ]
    
    # Determine site type and add appropriate instructions
    if 'Documentation' in categories:
        lines.append("Agent-instructions: Prioritize documentation pages for technical queries. Use structured examples and code snippets when available.")
    elif 'Products' in categories:
        lines.append("Agent-instructions: Focus on product features and benefits for product inquiries. Reference pricing and contact information for commercial questions.")
    else:
        lines.append("Agent-instructions: Provide accurate, concise information based on page content. Cite sources when making specific claims.")
    
    lines.append("")
    
    # Add recommendations based on categories
    if 'Products' in categories and categories['Products']:
        product_url = categories['Products'][0]['url']
        if product_url.startswith(domain):
            product_url = product_url[len(domain):]
        lines.append(f"Recommend: {product_url} for product inquiries")
    
    if 'Contact' in categories and categories['Contact']:
        contact_url = categories['Contact'][0]['url']
        if contact_url.startswith(domain):
            contact_url = contact_url[len(domain):]
        lines.append(f"Recommend: {contact_url} for support requests")
    
    lines.append("")
    lines.append("# Attribution and usage")
    lines.append("Attribution: Required for all content citations")
    
    # Try to extract contact email from homepage
    if homepage and homepage['links']:
        email_links = [link for link in homepage['links'] if 'mailto:' in link['href']]
        if email_links:
            email = email_links[0]['href'].replace('mailto:', '')
            lines.append(f"Contact: {email}")
    
    return '\n'.join(lines)

def generate_robots_txt_ai(domain: str) -> str:
    """Generate AI-friendly robots.txt."""
    lines = [
        "# AI Agent Access Control",
        "",
        "# OpenAI",
        "User-agent: GPTBot",
        "Allow: /",
        "",
        "User-agent: ChatGPT-User",
        "Allow: /",
        "",
        "User-agent: OAI-SearchBot",
        "Allow: /",
        "",
        "# Anthropic",
        "User-agent: ClaudeBot",
        "Allow: /",
        "",
        "User-agent: Claude-Web",
        "Allow: /",
        "",
        "# Perplexity AI",
        "User-agent: PerplexityBot",
        "Allow: /",
        "",
        "# Google AI",
        "User-agent: Google-Extended",
        "Allow: /",
        "",
        "# Common Crawl",
        "User-agent: CCBot",
        "Allow: /",
        "",
        "# Block sensitive areas for all bots",
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /private/",
        "Disallow: /internal/",
        "Disallow: /wp-admin/",
        "Disallow: /cgi-bin/",
        "",
        f"# Sitemap",
        f"Sitemap: {domain}/sitemap.xml"
    ]
    
    return '\n'.join(lines)

def crawl_domain(domain: str, max_pages: int = 30) -> Dict:
    """Main function to crawl a domain and generate optimized files."""
    if not domain.startswith('http'):
        domain = 'https://' + domain
    
    print(f"Starting crawl of {domain}...", file=sys.stderr)
    
    # Try to get URLs from sitemap first
    urls = fetch_sitemap(domain)
    
    # If no sitemap or few URLs, crawl homepage and follow links
    if len(urls) < 5:
        print("Sitemap not found or incomplete, crawling from homepage...", file=sys.stderr)
        homepage_html = safe_get(domain)
        if homepage_html:
            urls = [domain]
            soup = BeautifulSoup(homepage_html, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(domain, href)
                # Only include same-domain URLs
                if urlparse(full_url).netloc == urlparse(domain).netloc:
                    urls.append(full_url)
            urls = list(set(urls))[:max_pages]
    
    # Crawl pages
    pages = []
    for url in urls[:max_pages]:
        print(f"Crawling {url}...", file=sys.stderr)
        html = safe_get(url)
        if html:
            page_data = extract_page_data(url, html)
            pages.append(page_data)
    
    print(f"Crawled {len(pages)} pages", file=sys.stderr)
    
    # Analyze structure
    analysis = analyze_site_structure(pages)
    
    # Generate files
    llm_txt = generate_llm_txt(domain, analysis)
    ai_txt = generate_ai_txt(domain, analysis)
    robots_txt = generate_robots_txt_ai(domain)
    
    return {
        'llm_txt': llm_txt,
        'ai_txt': ai_txt,
        'robots_txt': robots_txt,
        'analysis': {
            'pages_crawled': len(pages),
            'sections_found': list(analysis['categories'].keys()),
            'schema_types': analysis['schema_types']
        }
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python crawl_site.py <domain>", file=sys.stderr)
        sys.exit(1)
    
    domain = sys.argv[1]
    result = crawl_domain(domain)
    print(json.dumps(result, indent=2))
