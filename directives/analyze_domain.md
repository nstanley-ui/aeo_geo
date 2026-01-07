# Directive: Analyze Domain for AEO/GEO

## Goal
Determine how well a domain is structured for discovery by AI agents and large language models.

## Inputs
- `domain`: The target domain (e.g., `ironhorse.io`)

## Analysis Steps
1. **Check for `llm.txt`**: Look for the file at `https://<domain>/llm.txt`. This file provides guidance to LLMs on how to consume the site's content.
2. **Check for `ai.txt`**: Look for semantic definitions or specific bot instructions at `https://<domain>/ai.txt`.
3. **Check robots.txt**: Verify if common AI crawlers (GPTBot, Claude-bot, PerplexityBot) are allowed or blocked.
4. **Metadata Audit**: Check for Schema.org markup (specifically `Organization`, `Product`, `Service`) that helps engines understand entities.

## Output
- JSON report with:
    - Discovery status for `llm.txt` and `ai.txt`.
    - AI Crawler permission status.
    - SEO/Entity score based on metadata findings.
    - Actionable recommendations.
