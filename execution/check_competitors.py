import json
import sys
import random

def check_competitors(domain):
    # Simulating a competitor search and analysis
    competitors = [
        {"name": "Competitor Alpha", "domain": "alpha-tech.io", "score": random.randint(40, 85)},
        {"name": "Competitor Beta", "domain": "beta-solutions.com", "score": random.randint(35, 75)},
        {"name": "Competitor Gamma", "domain": "gamma-global.net", "score": random.randint(50, 90)},
        {"name": "Competitor Delta", "domain": "delta-services.co", "score": random.randint(20, 60)},
        {"name": "Competitor Epsilon", "domain": "epsilon-labs.ai", "score": random.randint(45, 80)},
    ]
    
    # Sort by score for better visualization
    competitors.sort(key=lambda x: x['score'], reverse=True)
    
    return {
        "target_domain": domain,
        "competitors": competitors
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "ironhorse.io"
    print(json.dumps(check_competitors(target), indent=2))
