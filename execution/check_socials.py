import json
import sys
import random

def audit_socials(domain):
    # In a real app, we would search LinkedIn, Crunchbase, etc.
    # For this demo, we'll derive some data from the domain and randomize some scores.
    
    brand_name = domain.split('.')[0].capitalize()
    
    platforms = [
        {
            "name": "LinkedIn",
            "score": random.randint(40, 90),
            "status": "Found",
            "tips": ["Post more frequently", "Encourage employees to link profiles"]
        },
        {
            "name": "Crunchbase",
            "score": random.randint(30, 85),
            "status": "Found",
            "tips": ["Add recent funding rounds", "Complete the team section"]
        },
        {
            "name": "Reddit",
            "score": random.randint(20, 75),
            "status": "Monitored",
            "tips": ["Engage with community threads", "Monitor brand sentiment"]
        }
    ]
    
    overall_score = sum(p["score"] for p in platforms) // len(platforms)
    
    return {
        "brand": brand_name,
        "overall_social_score": overall_score,
        "platforms": platforms
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "ironhorse.io"
    print(json.dumps(audit_socials(target), indent=2))
