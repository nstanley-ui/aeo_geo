# Directive: Social and Professional Profile Audit

## Goal
Evaluate the visibility and favorability of a company's entities on professional and social platforms.

## Inputs
- `company_name`: Name of the company.
- `crunchbase_url`: (Optional)
- `linkedin_url`: (Optional)

## Analysis Steps
1. **Crunchbase Check**:
    - Verify if the profile is "Verified".
    - Check for completeness of "About" section and key personnel lists.
2. **LinkedIn Audit**:
    - Check for regular posting cadence.
    - Verify employee count and "About" section clarity for AI scrapers.
3. **Reddit Sentiment Simulation**:
    - Search for mentions on Reddit.
    - Evaluate overall sentiment (Positive/Neutral/Negative).
    - Identify common "themes" associated with the brand by the community.

## Output
- JSON report with:
    - Score for each platform (0-100).
    - Aggregate "Social Visibility Score".
    - Targeted suggestions for profile improvement.
