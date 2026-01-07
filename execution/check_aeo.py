import requests
from bs4 import BeautifulSoup
import json
import sys

# Update: Accept entity_type argument
def check_domain(domain, entity_type="Organization"):
    if not domain.startswith("http"):
        domain = "https://" + domain
    
    report = {
        "domain": domain,
        "llm_txt": {"exists": False, "content": None, "grade": "Missing", "filename": "llms.txt"},
        "ai_txt": {"exists": False, "content": None},
        "robots_txt": {"exists": False, "content": None, "ai_friendly": False},
        "metadata": {"schema_org": False, "description": None, "entity_detected": None},
        "aeo_score": 0,
        "recommendations": []
    }

    # Helper to fetch with better headers
    def safe_get(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        try:
            r = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
            if r.status_code == 200:
                return r.text
        except:
            pass
        return None

    grading_criteria = {
        "llm_txt": {
            "Great": {"score": 90, "criteria": "1000+ chars, 3+ sections (About, Products, Docs), 10+ links"},
            "Good": {"score": 70, "criteria": "500-1000 chars, 2+ sections, 5-10 links"},
            "Average": {"score": 50, "criteria": "200-500 chars, basic structure"},
            "Poor": {"score": 20, "criteria": "<200 chars, incomplete"},
            "Missing": {"score": 0, "criteria": "File not found"}
        },
        "ai_txt": {
            "Great": {"score": 90, "criteria": "Has Agent-instructions, attribution, contact info"},
            "Good": {"score": 70, "criteria": "Has Agent-instructions"},
            "Average": {"score": 50, "criteria": "Basic structure"},
            "Poor": {"score": 20, "criteria": "<50 chars"},
            "Missing": {"score": 0, "criteria": "File not found"}
        },
        "robots_txt": {
            "Great": {"score": 90, "criteria": "Allows 3+ AI bots (GPT, Claude, Perplexity)"},
            "Good": {"score": 70, "criteria": "Allows 1-2 AI bots"},
            "Average": {"score": 50, "criteria": "Generic rules"},
            "Poor": {"score": 20, "criteria": "Blocks AI agents"},
            "Missing": {"score": 0, "criteria": "File not found"}
        }
    }

    def evaluate_quality(content, file_type):
        if not content:
            return {"grade": "Missing", "criteria": grading_criteria[file_type]["Missing"]}
        
        length = len(content)
        if file_type == "llm_txt":
            if length > 1000: return {"grade": "Great", "criteria": grading_criteria[file_type]["Great"]}
            if length > 500: return {"grade": "Good", "criteria": grading_criteria[file_type]["Good"]}
            if length > 200: return {"grade": "Average", "criteria": grading_criteria[file_type]["Average"]}
            return {"grade": "Poor", "criteria": grading_criteria[file_type]["Poor"]}
        elif file_type == "ai_txt":
            if "Agent-instructions" in content and length > 200: return {"grade": "Great", "criteria": grading_criteria[file_type]["Great"]}
            if length > 100: return {"grade": "Good", "criteria": grading_criteria[file_type]["Good"]}
            if length > 50: return {"grade": "Average", "criteria": grading_criteria[file_type]["Average"]}
            return {"grade": "Poor", "criteria": grading_criteria[file_type]["Poor"]}
        elif file_type == "robots_txt":
            ai_bots = ["GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended"]
            bot_count = sum(1 for bot in ai_bots if bot in content)
            if any(f"User-agent: {bot}" in content and "Disallow: /" in content for bot in ai_bots):
                return {"grade": "Poor", "criteria": grading_criteria[file_type]["Poor"]}
            if bot_count >= 3: return {"grade": "Great", "criteria": grading_criteria[file_type]["Great"]}
            if bot_count >= 1: return {"grade": "Good", "criteria": grading_criteria[file_type]["Good"]}
            if "User-agent" in content: return {"grade": "Average", "criteria": grading_criteria[file_type]["Average"]}
            return {"grade": "Poor", "criteria": grading_criteria[file_type]["Poor"]}
        return {"grade": "Average", "criteria": {}}

    # 1. Check llms.txt (Plural - Standard) AND llm.txt (Singular - Legacy)
    llms_content = safe_get(f"{domain}/llms.txt")
    llm_singular_content = safe_get(f"{domain}/llm.txt")

    if llms_content:
        report["llm_txt"]["exists"] = True
        report["llm_txt"]["content"] = llms_content
        report["llm_txt"]["filename"] = "llms.txt"
        report["aeo_score"] += 30
    elif llm_singular_content:
        report["llm_txt"]["exists"] = True
        report["llm_txt"]["content"] = llm_singular_content
        report["llm_txt"]["filename"] = "llm.txt"
        report["aeo_score"] += 30
        report["recommendations"].append("Rename llm.txt to llms.txt to match the emerging standard.")
    else:
        report["recommendations"].append("Create an llms.txt file to guide AI agents.")
    
    content_to_grade = llms_content if llms_content else llm_singular_content
    quality_result = evaluate_quality(content_to_grade, "llm_txt")
    report["llm_txt"]["grade"] = quality_result["grade"]

    # 2. Check ai.txt
    ai_content = safe_get(f"{domain}/ai.txt")
    if ai_content:
        report["ai_txt"]["exists"] = True
        report["ai_txt"]["content"] = ai_content
        report["aeo_score"] += 20
    else:
        report["recommendations"].append("Consider adding an ai.txt for specific bot instructions.")
    quality_result = evaluate_quality(ai_content, "ai_txt")
    report["ai_txt"]["grade"] = quality_result["grade"]

    # 3. Check robots.txt
    robots_content = safe_get(f"{domain}/robots.txt")
    if robots_content:
        report["robots_txt"]["exists"] = True
        report["robots_txt"]["content"] = robots_content
        if any(bot in robots_content for bot in ["GPTBot", "ClaudeBot", "PerplexityBot"]):
            report["robots_txt"]["ai_friendly"] = True
            report["aeo_score"] += 10
    else:
        report["recommendations"].append("Optimize robots.txt to explicitly allow AI crawlers.")
    quality_result = evaluate_quality(robots_content, "robots_txt")
    report["robots_txt"]["grade"] = quality_result["grade"]
    
    # 4. Check metadata (Context Aware!)
    base_html = safe_get(domain)
    if base_html:
        soup = BeautifulSoup(base_html, 'html.parser')
        scripts = soup.find_all("script", type="application/ld+json")
        
        # Check based on Entity Type selection
        target_schema = "Product" if entity_type == "Product" else "Organization"
        
        found_target_schema = False
        if scripts:
            for s in scripts:
                if target_schema in s.text:
                    found_target_schema = True
                    break
            
            if found_target_schema:
                report["metadata"]["schema_org"] = True
                report["metadata"]["entity_detected"] = target_schema
                report["aeo_score"] += 20
            else:
                report["recommendations"].append(f"Add Schema.org '{target_schema}' markup (you selected {entity_type}).")
        else:
            report["recommendations"].append(f"Add Schema.org JSON-LD markup for {target_schema}.")

    report["aeo_score"] = min(report["aeo_score"], 100)
    
    return report
