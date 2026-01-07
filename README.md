# MOJO AEO GEO CHECKER

A powerful tool for analyzing your company's visibility in the AI Agent Economy (AEO). This application audits your domain for AI-agent-facing infrastructure and provides actionable recommendations.

![MOJO AEO GEO CHECKER](screenshot.png)

## Features

- **Agent Mojo Score**: Composite visibility score based on multiple factors
- **Infrastructure Audit**: Checks for llm.txt, ai.txt, and robots.txt files
- **Content Analysis**: Evaluates answer-first approach, entity definitions, and schema markup
- **Social Favorability**: Analyzes presence on LinkedIn, Crunchbase, and Reddit
- **Competitor Benchmarking**: Compare your AEO score with competitors
- **File Generation**: Automatically generates optimized AEO files by crawling your site

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **BeautifulSoup4**: HTML parsing and web scraping
- **Requests**: HTTP library for web requests

### Frontend
- **React 19**: Latest React with hooks
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool
- **Framer Motion**: Smooth animations
- **Recharts**: Beautiful data visualizations
- **Lucide React**: Icon library

## Installation

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Frontend Setup

1. Navigate to the UI directory:
```bash
cd ui
```

2. Install Node dependencies:
```bash
npm install
```

## Running the Application

### Option 1: Manual Start

**Terminal 1 - Backend:**
```bash
python server.py
```
The backend will run on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd ui
npm run dev
```
The frontend will run on `http://localhost:5173`

### Option 2: Using the Start Script (Recommended)

```bash
python start.py
```

This will start both the backend and frontend servers automatically.

## Usage

1. Open your browser and navigate to `http://localhost:5173` (or the port shown by Vite)
2. Enter a domain name (e.g., `ironhorse.io`)
3. Click **"Run Domain Audit"** to analyze the domain
4. View the results including:
   - Agent Mojo Score
   - Infrastructure grades (llm.txt, ai.txt, robots.txt)
   - Advanced content checks
   - Social media presence
5. Click **"Generate Optimized AEO Files"** to create custom files for your domain
6. Download the generated files and implement them on your website

## API Endpoints

### `GET /analyze?domain={domain}`
Analyzes a domain for AEO compliance and returns a comprehensive report.

**Response:**
```json
{
  "domain": "example.com",
  "overall_score": 65,
  "aeo": {
    "aeo_score": 70,
    "llm_txt": { ... },
    "ai_txt": { ... },
    "robots_txt": { ... }
  },
  "social": {
    "overall_social_score": 60,
    "platforms": [ ... ]
  }
}
```

### `GET /competitors?domain={domain}`
Returns competitor analysis for benchmarking.

### `GET /generate-files?domain={domain}`
Crawls the domain and generates optimized AEO files (llm.txt, ai.txt, robots.txt).

## Grading System

### llm.txt
- **Great (90 pts)**: 1000+ chars, comprehensive sections, 10+ well-organized links
- **Good (70 pts)**: 500-1000 chars, 2+ sections, 5-10 links
- **Average (50 pts)**: 200-500 chars, basic structure, 2-5 links
- **Poor (20 pts)**: <200 chars or missing

### ai.txt
- **Great (90 pts)**: Agent-instructions, attribution requirements, contact info
- **Good (70 pts)**: Agent-instructions and basic directives
- **Average (50 pts)**: Basic structure with minimal instructions
- **Poor (20 pts)**: Missing or minimal content

### robots.txt
- **Great (90 pts)**: Explicitly allows 3+ AI bots (GPTBot, ClaudeBot, PerplexityBot)
- **Good (70 pts)**: Allows some AI bots
- **Average (50 pts)**: Generic rules, no AI-specific directives
- **Poor (20 pts)**: Missing or blocks AI agents

## Project Structure

```
AEO GEO Checker/
├── server.py              # FastAPI backend server
├── requirements.txt       # Python dependencies
├── execution/
│   ├── check_aeo.py      # AEO infrastructure checks
│   ├── check_socials.py  # Social media presence audit
│   ├── check_competitors.py  # Competitor analysis
│   └── crawl_site.py     # Site crawler and file generator
├── directives/           # Agent prompt directives
└── ui/                   # React frontend
    ├── src/
    │   ├── App.tsx       # Main application component
    │   ├── App.css       # Component styles
    │   └── index.css     # Global styles
    ├── package.json      # Node dependencies
    └── vite.config.ts    # Vite configuration
```

## Development

### Backend Development
The backend uses FastAPI with subprocess calls to Python scripts for modular analysis.

### Frontend Development
The frontend uses React with TypeScript. Key components:
- Main analysis interface
- Grading modal for detailed criteria
- File generation modal
- Competitor benchmarking

To build for production:
```bash
cd ui
npm run build
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

- Built with [Antigravity](https://antigravity.com) for rapid development
- Inspired by the growing importance of AI Agent Economy optimization
- Special thanks to the AEO community for establishing standards

## What's Next?

- [ ] Integration with real social media APIs
- [ ] More sophisticated competitor analysis
- [ ] AI-powered recommendations
- [ ] Export reports to PDF
- [ ] Historical tracking of AEO scores
- [ ] Multi-domain bulk analysis
