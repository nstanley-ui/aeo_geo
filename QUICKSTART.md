# Quick Start Guide

Get your MOJO AEO GEO CHECKER up and running in minutes!

## Prerequisites Check

Before starting, make sure you have:
- ✅ Python 3.8 or higher: `python3 --version`
- ✅ Node.js 18 or higher: `node --version`
- ✅ npm or yarn: `npm --version`

## 5-Minute Setup

### Step 1: Install Dependencies

**Python (Backend):**
```bash
pip install -r requirements.txt
```

**Node.js (Frontend):**
```bash
cd ui
npm install
cd ..
```

### Step 2: Start the Application

**Option A - Single Command (Recommended):**
```bash
# Linux/Mac
./start.sh

# Windows/Cross-platform
python start.py
```

**Option B - Manual (Two Terminals):**

Terminal 1 (Backend):
```bash
python server.py
# Backend runs on http://localhost:8000
```

Terminal 2 (Frontend):
```bash
cd ui
npm run dev
# Frontend runs on http://localhost:5173
```

### Step 3: Open in Browser

Navigate to: **http://localhost:5173**

## First Test Run

1. The app opens with `ironhorse.io` as the default domain
2. Click **"Run Domain Audit"** 
3. Wait ~5-10 seconds for the analysis
4. View your results!

## Understanding Your Results

### Agent Mojo Score (0-100)
Your composite visibility score in the AI Agent Economy. Higher is better!

- **80-100**: Excellent - You're AEO optimized!
- **60-79**: Good - Solid foundation, room for improvement
- **40-59**: Average - Critical infrastructure missing
- **0-39**: Poor - Invisible to AI agents

### Infrastructure Checks

**llm.txt** - Your AI agent sitemap
- **Great**: Comprehensive, well-structured content
- **Good**: Decent coverage, could expand
- **Average**: Basic information present
- **Poor**: Missing or minimal

**ai.txt** - Agent-specific directives
- Provides instructions for AI agents on how to use your content

**robots.txt** - Crawler access control
- Should explicitly allow AI agent bots (GPTBot, ClaudeBot, etc.)

### Advanced Content Checks

- **answer first**: Direct answers in leading content
- **explicit entities**: Clear entity definitions (Organization, Product)
- **single intent**: Focused page purpose
- **advanced schema**: Rich structured data (FAQ, HowTo, etc.)

## Next Steps

### Download Optimized Files
1. Click **"Generate Optimized AEO Files"**
2. The system will crawl your site (takes 30-60 seconds)
3. Download the generated files:
   - `llm.txt`
   - `ai.txt`
   - `robots.txt`
4. Upload these to your website's root directory

### Check Competitors
1. Click **"Benchmarking"** to see how you stack up
2. Compare your score with similar companies
3. Identify areas for improvement

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use: `lsof -i :8000` (Mac/Linux)
- Verify Python dependencies: `pip list | grep fastapi`

### Frontend won't start
- Check if port 5173 is available
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf ui/node_modules && cd ui && npm install`

### "Connection refused" errors
- Make sure the backend is running first
- Check that both servers are on the expected ports
- Try accessing backend directly: http://localhost:8000/analyze?domain=ironhorse.io

### Slow analysis
- Normal for first run (cold start)
- Large sites take longer to crawl
- Check your internet connection

## Development Mode

### Hot Reload
Both backend and frontend support hot reload:
- **Backend**: FastAPI auto-reloads on file changes
- **Frontend**: Vite provides instant HMR (Hot Module Replacement)

### Making Changes

**Backend Changes:**
1. Edit files in `execution/` directory
2. Changes auto-reload (FastAPI's `--reload` flag)

**Frontend Changes:**
1. Edit `ui/src/App.tsx` or other components
2. See changes instantly in browser

### Build for Production

```bash
cd ui
npm run build
```

Outputs to `ui/dist/` directory.

## API Testing

Test the API directly with curl:

```bash
# Check a domain
curl "http://localhost:8000/analyze?domain=ironhorse.io" | jq

# Get competitors
curl "http://localhost:8000/competitors?domain=ironhorse.io" | jq

# Generate files
curl "http://localhost:8000/generate-files?domain=ironhorse.io" | jq
```

## Common Use Cases

### 1. Pre-Launch Audit
Check your site before going live:
```
1. Run audit on staging domain
2. Download optimized files
3. Implement before production deploy
```

### 2. Competitor Research
```
1. Run audits on top 5 competitors
2. Note their scores and approaches
3. Identify gaps in your strategy
```

### 3. Ongoing Monitoring
```
1. Run weekly audits
2. Track score changes over time
3. Validate new content additions
```

## Tips for Best Results

1. **Run on production domain** - Staging may have robots.txt blocking crawlers
2. **Test multiple pages** - The generator crawls up to 30 pages
3. **Keep files updated** - Regenerate when site structure changes
4. **Monitor regularly** - AEO is an ongoing process
5. **Learn from competition** - Check high-scoring sites for inspiration

## Support

Need help? Check:
- Full README.md for detailed documentation
- GitHub Issues for known problems
- Documentation at project wiki

Happy AEO optimizing! 🚀
