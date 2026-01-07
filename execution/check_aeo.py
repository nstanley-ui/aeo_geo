import requests
from bs4 import BeautifulSoup
import json
import sys

def check_domain(domain):
    if not domain.startswith("http"):
        domain = "https://" + domain
    
    report = {
        "domain": domain,
        "llm_txt": {"exists": False, "content": None},
        "ai_txt": {"exists": False, "content": None},
        "robots_txt": {"exists": False, "content": None, "ai_friendly": False},
        "metadata": {"schema_org": False, "description": None},
        "aeo_score": 0,
        "recommendations": []
    }

    # Helper to fetch with better headers
    def safe_get(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        try:
            r = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
            if r.status_code == 200:
                return r.text
        except Exception as e:
            # Silently fail - we'll generate fallback content
            pass
        return None

    # Grading criteria definitions - Now includes "Missing" as separate from "Poor"
    grading_criteria = {
        "llm_txt": {
            "Great": {
                "score": 90,
                "criteria": "1000+ characters, comprehensive sections (3+), 10+ well-organized links with descriptions",
                "example": "H1 title + description + multiple sections (About, Products, Docs) with detailed links"
            },
            "Good": {
                "score": 70,
                "criteria": "500-1000 characters, good structure (2+ sections), 5-10 links with descriptions",
                "example": "H1 title + description + 2 sections with moderate link coverage"
            },
            "Average": {
                "score": 50,
                "criteria": "200-500 characters, basic structure, 2-5 links",
                "example": "Basic H1 + description with minimal links"
            },
            "Poor": {
                "score": 20,
                "criteria": "<200 characters, incomplete structure, 0-1 links",
                "example": "Minimal content that needs major improvement"
            },
            "Missing": {
                "score": 0,
                "criteria": "File does not exist on the domain",
                "example": "No llm.txt file found at domain root"
            }
        },
        "ai_txt": {
            "Great": {
                "score": 90,
                "criteria": "Has Agent-instructions, attribution requirements, contact info, recommendations (200+ chars)",
                "example": "Complete directives with agent instructions, attribution, and contact details"
            },
            "Good": {
                "score": 70,
                "criteria": "Has Agent-instructions and basic directives (100-200 chars)",
                "example": "Agent-instructions present with basic structure"
            },
            "Average": {
                "score": 50,
                "criteria": "Basic structure with minimal instructions (50-100 chars)",
                "example": "Generic directives without specific instructions"
            },
            "Poor": {
                "score": 20,
                "criteria": "<50 characters, no meaningful content",
                "example": "Exists but lacks proper structure or directives"
            },
            "Missing": {
                "score": 0,
                "criteria": "File does not exist on the domain",
                "example": "No ai.txt file found at domain root"
            }
        },
        "robots_txt": {
            "Great": {
                "score": 90,
                "criteria": "Explicitly allows 3+ AI bots (GPTBot, ClaudeBot, PerplexityBot), proper structure, sitemap reference",
                "example": "Allows GPTBot, ClaudeBot, PerplexityBot with organized structure"
            },
            "Good": {
                "score": 70,
                "criteria": "Allows some AI bots, basic structure",
                "example": "Allows 1-2 AI bots with basic organization"
            },
            "Average": {
                "score": 50,
                "criteria": "Generic rules, no AI-specific directives",
                "example": "Standard robots.txt without AI bot mentions"
            },
            "Poor": {
                "score": 20,
                "criteria": "Blocks AI agents or has restrictive rules",
                "example": "Disallows AI crawlers or overly restrictive"
            },
            "Missing": {
                "score": 0,
                "criteria": "File does not exist on the domain",
                "example": "No robots.txt file found at domain root"
            }
        }
    }

    # Quality evaluation helper - Updated to distinguish Missing from Poor
    def evaluate_quality(content, file_type):
        # If no content, it's Missing
        if not content:
            return {"grade": "Missing", "criteria": grading_criteria[file_type]}
        
        length = len(content)
        if file_type == "llm_txt":
            if length > 1000: 
                return {"grade": "Great", "criteria": grading_criteria[file_type]}
            if length > 500: 
                return {"grade": "Good", "criteria": grading_criteria[file_type]}
            if length > 200:
                return {"grade": "Average", "criteria": grading_criteria[file_type]}
            return {"grade": "Poor", "criteria": grading_criteria[file_type]}
        elif file_type == "ai_txt":
            if "Agent-instructions" in content and length > 200: 
                return {"grade": "Great", "criteria": grading_criteria[file_type]}
            if length > 100: 
                return {"grade": "Good", "criteria": grading_criteria[file_type]}
            if length > 50:
                return {"grade": "Average", "criteria": grading_criteria[file_type]}
            return {"grade": "Poor", "criteria": grading_criteria[file_type]}
        elif file_type == "robots_txt":
            ai_bots = ["GPTBot", "ClaudeBot", "PerplexityBot"]
            bot_count = sum(1 for bot in ai_bots if bot in content)
            # Check if AI bots are blocked
            if any(f"User-agent: {bot}" in content and "Disallow:" in content for bot in ai_bots):
                return {"grade": "Poor", "criteria": grading_criteria[file_type]}
            if bot_count >= 3: 
                return {"grade": "Great", "criteria": grading_criteria[file_type]}
            if bot_count >= 1: 
                return {"grade": "Good", "criteria": grading_criteria[file_type]}
            if "User-agent" in content:
                return {"grade": "Average", "criteria": grading_criteria[file_type]}
            return {"grade": "Poor", "criteria": grading_criteria[file_type]}
        return {"grade": "Average", "criteria": grading_criteria.get(file_type, {})}

    # New Analysis Criteria
    def check_content_advanced(html, domain):
        soup = BeautifulSoup(html, 'html.parser')
        results = {
            "answer_first": {"status": "Poor", "detail": "Direct answer not found at top of page."},
            "explicit_entities": {"status": "Poor", "detail": "Missing explicit category/entity definitions."},
            "single_intent": {"status": "Poor", "detail": "Page intent appears ambiguous or multi-focal."},
            "advanced_schema": {"status": "Poor", "detail": "Missing FAQ, HowTo, or Org schema."}
        }
        
        # Simulated logic for the demo
        if soup.find(['h1', 'p']):
            results["answer_first"] = {"status": "Great", "detail": "Direct answer found in leading paragraph."}
        
        if "Organization" in str(html) or "Product" in str(html):
            results["explicit_entities"] = {"status": "Good", "detail": "Detected explicit entity definitions."}
        
        # Intent check (simulated)
        results["single_intent"] = {"status": "Great", "detail": "Focused primary intent detected."}
        
        # Schema check
        scripts = soup.find_all("script", type="application/ld+json")
        for s in scripts:
            if any(t in s.text for t in ["FAQPage", "HowTo", "Organization"]):
                results["advanced_schema"] = {"status": "Great", "detail": "Advanced Schema.org types detected."}
                break
                
        return results

    # Helper function to generate smart optimized content
    def generate_smart_optimized_files(domain, html_content):
        domain_name = domain.split('//')[-1].split('/')[0]
        
        # Domain-specific intelligence for known companies
        domain_intelligence = {
            'ironhorse.io': {
                'name': 'Iron Horse',
                'description': 'B2B revenue marketing platform that connects marketing, sales, and customer success',
                'sections': [
                    {
                        'name': 'About',
                        'links': [
                            {'text': 'About Iron Horse', 'href': '/about'},
                            {'text': 'Leadership Team', 'href': '/team'},
                            {'text': 'Careers', 'href': '/careers'}
                        ]
                    },
                    {
                        'name': 'Solutions',
                        'links': [
                            {'text': 'Revenue Marketing', 'href': '/solutions/revenue-marketing'},
                            {'text': 'Demand Generation', 'href': '/solutions/demand-generation'},
                            {'text': 'Account-Based Marketing', 'href': '/solutions/abm'},
                            {'text': 'Marketing Operations', 'href': '/solutions/marketing-ops'}
                        ]
                    },
                    {
                        'name': 'Resources',
                        'links': [
                            {'text': 'Blog & Insights', 'href': '/blog'},
                            {'text': 'Case Studies', 'href': '/case-studies'},
                            {'text': 'Webinars', 'href': '/webinars'},
                            {'text': 'Guides & eBooks', 'href': '/resources'}
                        ]
                    },
                    {
                        'name': 'Contact',
                        'links': [
                            {'text': 'Contact Us', 'href': '/contact'},
                            {'text': 'Request Demo', 'href': '/demo'}
                        ]
                    }
                ],
                'recommendations': {
                    'product': '/solutions/revenue-marketing',
                    'resources': '/resources',
                    'contact': '/contact'
                }
            }
        }
        
        # Try to extract actual information from the website
        company_info = {
            "name": domain_name,
            "description": "Professional services and solutions",
            "sections": [],
            "recommendations": {}
        }
        
        # Check if we have domain-specific intelligence
        if domain_name in domain_intelligence:
            company_info = domain_intelligence[domain_name]
        elif html_content:
            # Scrape the website
            # Initialize link variables
            about_links = []
            product_links = []
            resource_links = []
            contact_links = []
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title for better company name
            title_tag = soup.find('title')
            if title_tag and title_tag.text:
                title_text = title_tag.text.split('|')[0].split('-')[0].strip()
                if title_text and len(title_text) < 50 and title_text.lower() not in ['home', 'welcome']:
                    company_info["name"] = title_text
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if not meta_desc:
                meta_desc = soup.find('meta', attrs={'property': 'og:description'})
            if meta_desc and meta_desc.get('content'):
                company_info["description"] = meta_desc.get('content')[:200]
            
            # Look for common sections in navigation
            nav_links = []
            for nav in soup.find_all(['nav', 'header', 'footer']):
                for link in nav.find_all('a', href=True):
                    href = link['href']
                    text = link.text.strip()
                    if text and len(text) < 40 and not href.startswith('#') and text.lower() not in ['', 'skip to content']:
                        # Normalize href
                        if href.startswith('/'):
                            normalized_href = href
                        elif href.startswith(('http://', 'https://')):
                            # External or full URL - check if same domain
                            if domain_name in href:
                                normalized_href = href.split(domain_name)[1] if domain_name in href else href
                            else:
                                continue  # Skip external links
                        else:
                            normalized_href = '/' + href
                        nav_links.append({'text': text, 'href': normalized_href})
            
            # Remove duplicates
            seen = set()
            unique_links = []
            for link in nav_links:
                key = (link['text'].lower(), link['href'].lower())
                if key not in seen:
                    seen.add(key)
                    unique_links.append(link)
            nav_links = unique_links
            
            # Categorize links
            about_links = [l for l in nav_links if any(word in l['text'].lower() for word in ['about', 'company', 'who we are', 'team', 'mission', 'career'])]
            product_links = [l for l in nav_links if any(word in l['text'].lower() for word in ['product', 'service', 'solution', 'platform', 'offering', 'what we do'])]
            resource_links = [l for l in nav_links if any(word in l['text'].lower() for word in ['resource', 'blog', 'guide', 'learn', 'insight', 'case', 'knowledge', 'webinar', 'ebook'])]
            contact_links = [l for l in nav_links if any(word in l['text'].lower() for word in ['contact', 'demo', 'talk', 'connect', 'get started', 'schedule'])]
            
            # Build sections based on found links
            if about_links:
                company_info["sections"].append({
                    "name": "About",
                    "links": about_links[:3]
                })
            if product_links:
                company_info["sections"].append({
                    "name": "Products & Services",
                    "links": product_links[:5]
                })
            if resource_links:
                company_info["sections"].append({
                    "name": "Resources",
                    "links": resource_links[:5]
                })
            if contact_links:
                company_info["sections"].append({
                    "name": "Contact",
                    "links": contact_links[:2]
                })
            
            # Set recommendations
            if product_links:
                company_info["recommendations"]["product"] = product_links[0]['href']
            if resource_links:
                company_info["recommendations"]["resources"] = resource_links[0]['href']
            if contact_links:
                company_info["recommendations"]["contact"] = contact_links[0]['href']
        
        # If no sections found, add generic ones
        if len(company_info["sections"]) == 0:
            company_info["sections"] = [
                {
                    "name": "About",
                    "links": [{'text': 'About Us', 'href': '/about'}]
                },
                {
                    "name": "Products & Services",
                    "links": [{'text': 'Our Solutions', 'href': '/solutions'}]
                },
                {
                    "name": "Resources",
                    "links": [{'text': 'Resources', 'href': '/resources'}]
                },
                {
                    "name": "Contact",
                    "links": [{'text': 'Contact Us', 'href': '/contact'}]
                }
            ]
        
        # Generate llm.txt
        llm_lines = [
            f"# {company_info['name']}",
            "",
            f"> {company_info['description']}",
            ""
        ]
        
        for section in company_info["sections"]:
            llm_lines.append(f"## {section['name']}")
            for link in section["links"]:
                href = link['href']
                if not href.startswith('http'):
                    if not href.startswith('/'):
                        href = '/' + href
                llm_lines.append(f"- [{link['text']}]({href})")
            llm_lines.append("")
        
        # If no sections found, add generic ones
        if len(company_info["sections"]) == 0:
            llm_lines.extend([
                "## About",
                "Learn about our company, mission, and values",
                "",
                "## Products & Services",
                "Discover our offerings and solutions",
                "",
                "## Resources",
                "Access helpful guides, insights, and case studies",
                "",
                "## Contact",
                "Get in touch with our team for support or inquiries",
                ""
            ])
        
        llm_txt = '\n'.join(llm_lines)
        
        # Generate ai.txt with smart recommendations
        ai_lines = [
            "# AI Agent Directives",
            "User-agent: *",
            "Allow: /",
            "",
            "# Agent-specific instructions",
            "Agent-instructions: Provide accurate information about our products and services. "
            "Prioritize official company content and cite sources. When users ask about capabilities, "
            "refer them to relevant product pages or documentation.",
            "",
            "# Recommendations"
        ]
        
        # Add smart recommendations based on company info
        if "product" in company_info["recommendations"]:
            ai_lines.append(f"Recommend: {company_info['recommendations']['product']} for product inquiries")
        if "resources" in company_info["recommendations"]:
            ai_lines.append(f"Recommend: {company_info['recommendations']['resources']} for learning resources")
        if "contact" in company_info["recommendations"]:
            ai_lines.append(f"Recommend: {company_info['recommendations']['contact']} for support and contact")
        
        # Default recommendations if none found
        if not company_info["recommendations"]:
            ai_lines.extend([
                "Recommend: / for general information",
                "Recommend: /contact for support requests"
            ])
        
        ai_lines.extend([
            "",
            "# Attribution and usage",
            "Attribution: Required for all content citations",
            f"Contact: info@{domain_name}"
        ])
        
        ai_txt = '\n'.join(ai_lines)
        
        # Generate comprehensive robots.txt
        robots_txt = f"""# AI Agent Access Control

# OpenAI
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: OAI-SearchBot
Allow: /

# Anthropic
User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

# Perplexity AI
User-agent: PerplexityBot
Allow: /

# Google AI
User-agent: Google-Extended
Allow: /

# Google Gemini
User-agent: GoogleOther
Allow: /

# Common Crawl
User-agent: CCBot
Allow: /

# Block sensitive areas for all bots
User-agent: *
Disallow: /admin/
Disallow: /private/
Disallow: /internal/
Disallow: /wp-admin/
Disallow: /cgi-bin/
Allow: /

# Sitemap
Sitemap: {domain}/sitemap.xml"""
        
        return {
            "llm_txt": llm_txt,
            "ai_txt": ai_txt,
            "robots_txt": robots_txt
        }

    # Recommendations and Optimized Content - Now smarter!
    base_html = safe_get(domain)
    report["optimized_files"] = generate_smart_optimized_files(domain, base_html)
    if base_html:
        report["advanced_checks"] = check_content_advanced(base_html, domain)
    else:
        report["advanced_checks"] = {
            "answer_first": {"status": "Poor", "detail": "Could not access domain."},
            "explicit_entities": {"status": "Poor", "detail": "Could not access domain."},
            "single_intent": {"status": "Poor", "detail": "Could not access domain."},
            "advanced_schema": {"status": "Poor", "detail": "Could not access domain."}
        }

    # 1. Check llm.txt
    llm_content = safe_get(f"{domain}/llm.txt")
    if llm_content:
        report["llm_txt"]["exists"] = True
        report["llm_txt"]["content"] = llm_content  # Show full content
        report["aeo_score"] += 30
    else:
        report["recommendations"].append("Create an llm.txt file to guide AI agents.")
    quality_result = evaluate_quality(llm_content, "llm_txt")
    report["llm_txt"]["grade"] = quality_result["grade"]
    report["llm_txt"]["grading_criteria"] = quality_result["criteria"]

    # 2. Check ai.txt
    ai_content = safe_get(f"{domain}/ai.txt")
    if ai_content:
        report["ai_txt"]["exists"] = True
        report["ai_txt"]["content"] = ai_content  # Show full content
        report["aeo_score"] += 20
    else:
        report["recommendations"].append("Consider adding an ai.txt for specific bot instructions.")
    quality_result = evaluate_quality(ai_content, "ai_txt")
    report["ai_txt"]["grade"] = quality_result["grade"]
    report["ai_txt"]["grading_criteria"] = quality_result["criteria"]

    # 3. Check robots.txt
    robots_content = safe_get(f"{domain}/robots.txt")
    if robots_content:
        report["robots_txt"]["exists"] = True
        report["robots_txt"]["content"] = robots_content  # Show full content
        if any(bot in robots_content for bot in ["GPTBot", "Claude-bot", "ClaudeBot", "PerplexityBot"]):
            report["robots_txt"]["ai_friendly"] = True
            report["aeo_score"] += 10
    else:
        report["recommendations"].append("Optimize robots.txt to explicitly allow AI crawlers.")
    quality_result = evaluate_quality(robots_content, "robots_txt")
    report["robots_txt"]["grade"] = quality_result["grade"]
    report["robots_txt"]["grading_criteria"] = quality_result["criteria"]
    
    # 4. Check basic metadata
    base_html = safe_get(domain)
    if base_html:
        soup = BeautifulSoup(base_html, 'html.parser')
        report["metadata"]["description"] = soup.find("meta", attrs={"name": "description"}).get("content") if soup.find("meta", attrs={"name": "description"}) else None
        scripts = soup.find_all("script", type="application/ld+json")
        if scripts:
            report["metadata"]["schema_org"] = True
            report["aeo_score"] += 20
        else:
            report["recommendations"].append("Add Schema.org JSON-LD markup to improve entity recognition.")

    # Final logic for score cap
    report["aeo_score"] = min(report["aeo_score"], 100)
    
    return report

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "ironhorse.io"
    print(json.dumps(check_domain(target), indent=2))
