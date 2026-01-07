import React, { useState } from 'react';
import { Search, Globe, Users, TrendingUp, CheckCircle, XCircle, AlertTriangle, Cpu, FileText } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from 'recharts';

// --- Types ---
interface AnalysisResult {
  domain: string;
  overall_score: number;
  aeo: {
    aeo_score: number;
    llm_txt: { exists: boolean; content: string | null; grade: string; grading_criteria?: any };
    ai_txt: { exists: boolean; content: string | null; grade: string; grading_criteria?: any };
    robots_txt: { exists: boolean; content: string | null; ai_friendly: boolean; grade: string; grading_criteria?: any };
    recommendations: string[];
  };
  social: {
    overall_social_score: number;
    brand: string;
    platforms: Array<{ name: string; score: number; status: string; tips: string[] }>;
  };
  optimized_files: { llm_txt: string; ai_txt: string; robots_txt: string };
  advanced_checks: { [key: string]: { status: string; detail: string } };
}

interface CompetitorResult {
  target_domain: string;
  competitors: Array<{ name: string; domain: string; score: number }>;
}

interface GeneratedFiles {
  llm_txt: string;
  ai_txt: string;
  robots_txt: string;
  analysis: { pages_crawled: number; sections_found: string[]; schema_types: string[] };
}

// --- Helper Components ---

// Tip #3: Engine Status Card
const EngineCard: React.FC<{ name: string; status: 'Allowed' | 'Blocked' | 'Unknown'; detail: string }> = ({ name, status, detail }) => {
  const color = status === 'Allowed' ? 'text-green-600 bg-green-50' : status === 'Blocked' ? 'text-red-600 bg-red-50' : 'text-gray-600 bg-gray-50';
  const icon = status === 'Allowed' ? <CheckCircle size={18} /> : status === 'Blocked' ? <XCircle size={18} /> : <AlertTriangle size={18} />;
  
  return (
    <div className={`p-4 rounded-xl border border-gray-100 flex flex-col gap-2 ${color}`}>
      <div className="flex items-center justify-between">
        <span className="font-bold text-sm">{name}</span>
        {icon}
      </div>
      <span className="text-xs font-medium opacity-80">{detail}</span>
    </div>
  );
};

// --- Main App Component ---
const App: React.FC = () => {
  const [domain, setDomain] = useState('ironhorse.io');
  const [loading, setLoading] = useState(false);
  
  // Tip #1: Entity Confirmation State
  const [step, setStep] = useState<'input' | 'confirm' | 'results'>('input');
  const [entityData, setEntityData] = useState<{ name: string; type: string; domain: string }>({ name: '', type: 'Organization', domain: '' });

  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [competitors, setCompetitors] = useState<CompetitorResult | null>(null);
  const [compLoading, setCompLoading] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [generatedFiles, setGeneratedFiles] = useState<GeneratedFiles | null>(null);
  const [generateLoading, setGenerateLoading] = useState(false);

  // 1. Initial Fetch (Pre-Analysis)
  const handleInitialCheck = () => {
    if (!domain) return;
    // Simulate detecting entity from domain for Tip #1
    const detectedName = domain.split('.')[0].charAt(0).toUpperCase() + domain.split('.')[0].slice(1);
    setEntityData({ name: detectedName, type: 'Organization', domain: domain });
    setStep('confirm');
  };

  // 2. Confirm Entity & Run Full Analysis
  const handleConfirmAndAnalyze = async () => {
    setLoading(true);
    setStep('results');
    setResult(null);
    try {
      const resp = await fetch(`http://localhost:8000/analyze?domain=${domain}`);
      const data = await resp.json();
      setResult(data);
    } catch (err) {
      console.error("Analysis failed", err);
    } finally {
      setLoading(false);
    }
  };

  // Helper to parse robots.txt for Tip #3
  const getEngineStatus = (content: string | null, botName: string): { status: 'Allowed' | 'Blocked' | 'Unknown', detail: string } => {
    if (!content) return { status: 'Unknown', detail: 'No robots.txt found' };
    if (content.includes(`User-agent: ${botName}`) && content.includes("Disallow: /")) return { status: 'Blocked', detail: 'Explicitly blocked' };
    if (content.includes(`User-agent: ${botName}`) && content.includes("Allow: /")) return { status: 'Allowed', detail: 'Explicitly allowed' };
    return { status: 'Allowed', detail: 'Implicitly allowed (Wildcard)' }; // Default allow if not blocked
  };

  const downloadFile = (filename: string, content: string) => {
    const element = document.createElement("a");
    const file = new Blob([content], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = filename.endsWith('.txt') ? filename : `${filename}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handleGenerateFiles = async () => {
    setGenerateLoading(true);
    try {
      const resp = await fetch(`http://localhost:8000/generate-files?domain=${domain}`);
      const data = await resp.json();
      setGeneratedFiles(data);
      setShowGenerateModal(true);
    } catch (err) { console.error(err); } 
    finally { setGenerateLoading(false); }
  };

  const chartData = result ? [{ name: 'Overall', value: result.overall_score, fill: '#4f46e5' }] : [];

  return (
    <div className="min-h-screen p-4 lg:p-8">
      {/* Header */}
      <header className="mb-10 text-center max-w-4xl mx-auto pt-8">
        <h1 className="text-5xl font-black mb-3 vibrant-gradient-text tracking-tight">
          MOJO AEO CHECKER
        </h1>
        <p className="text-dim text-xl font-medium">
          Visibility Intelligence for the Agent Economy
        </p>
      </header>

      {/* STEP 1: Input */}
      {step === 'input' && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          className="glass-card max-w-3xl mx-auto p-10 flex flex-col gap-6"
        >
          <div className="relative w-full">
            <Search className="absolute left-5 top-5 text-dim" size={24} />
            <input
              type="text"
              className="pl-14 py-5 text-xl w-full font-medium"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              placeholder="Enter domain (e.g. ironhorse.io)"
              onKeyDown={(e) => e.key === 'Enter' && handleInitialCheck()}
            />
          </div>
          <button onClick={handleInitialCheck} className="btn-primary py-5 text-lg w-full">
            Start Audit
          </button>
        </motion.div>
      )}

      {/* STEP 2: Tip #1 Entity Confirmation */}
      {step === 'confirm' && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
          className="glass-card max-w-2xl mx-auto p-8 border-l-4 border-l-primary"
        >
          <h2 className="text-2xl font-bold mb-2">Confirm Entity Identity</h2>
          <p className="text-dim mb-6 text-sm">To ensure accurate scoring, please confirm how AI agents should identify this entity.</p>
          
          <div className="space-y-4 mb-8">
            <div>
              <label className="block text-xs font-bold uppercase text-dim mb-1">Brand Name</label>
              <input 
                type="text" value={entityData.name} 
                onChange={(e) => setEntityData({...entityData, name: e.target.value})}
                className="w-full p-3 bg-white/50 border border-gray-200 rounded-lg font-bold text-lg"
              />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase text-dim mb-1">Entity Type</label>
              <select 
                value={entityData.type}
                onChange={(e) => setEntityData({...entityData, type: e.target.value})}
                className="w-full p-3 bg-white/50 border border-gray-200 rounded-lg"
              >
                <option>Organization</option>
                <option>Product</option>
                <option>Person</option>
              </select>
            </div>
          </div>

          <div className="flex gap-4">
            <button onClick={() => setStep('input')} className="btn-secondary flex-1 py-3">Back</button>
            <button onClick={handleConfirmAndAnalyze} className="btn-primary flex-1 py-3 flex justify-center items-center gap-2">
              Confirm & Analyze <TrendingUp size={18} />
            </button>
          </div>
        </motion.div>
      )}

      {/* STEP 3: Results */}
      {step === 'results' && (
        <div className="max-w-[1600px] mx-auto">
          {loading ? (
            <div className="glass-card p-12 text-center">
              <div className="animate-spin w-12 h-12 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"/>
              <p className="text-lg font-medium text-dim">Analyzing agent visibility protocols...</p>
            </div>
          ) : result && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="grid grid-cols-12 gap-6">
              
              {/* Left Column: Score & Actions */}
              <div className="col-span-12 lg:col-span-3 space-y-6">
                <div className="glass-card p-8 flex flex-col items-center text-center">
                  <h3 className="text-lg font-bold mb-4 text-dim uppercase tracking-wider">Mojo Score</h3>
                  <div className="relative w-48 h-48 mb-4">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadialBarChart innerRadius="80%" outerRadius="100%" data={chartData} startAngle={180} endAngle={-180}>
                        <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
                        <RadialBar background dataKey="value" cornerRadius={30} fill="#4f46e5" />
                      </RadialBarChart>
                    </ResponsiveContainer>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-5xl font-black text-primary">{result.overall_score}</span>
                    </div>
                  </div>
                  <div className="w-full pt-6 border-t border-gray-100">
                    <button onClick={() => { setCompLoading(true); setTimeout(() => setCompLoading(false), 2000); }} disabled={compLoading} className="btn-secondary w-full py-3 text-sm flex items-center justify-center gap-2">
                      {compLoading ? 'Analyzing...' : 'Run Benchmarking'} <Users size={16}/>
                    </button>
                  </div>
                </div>

                <div className="glass-card p-6">
                   <h4 className="font-bold mb-4 flex items-center gap-2"><FileText size={20}/> Files Detected</h4>
                   <div className="space-y-3">
                     {[
                       {name: 'llm.txt', exists: result.aeo.llm_txt.exists, grade: result.aeo.llm_txt.grade},
                       {name: 'ai.txt', exists: result.aeo.ai_txt.exists, grade: result.aeo.ai_txt.grade},
                       {name: 'robots.txt', exists: result.aeo.robots_txt.exists, grade: result.aeo.robots_txt.grade},
                     ].map(f => (
                       <div key={f.name} className="flex justify-between items-center p-3 bg-white/50 rounded-lg border border-gray-100">
                         <span className="font-medium text-sm">{f.name}</span>
                         <span className={`text-xs font-bold px-2 py-1 rounded-full ${f.exists ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                           {f.exists ? f.grade : 'Missing'}
                         </span>
                       </div>
                     ))}
                   </div>
                   <button onClick={handleGenerateFiles} className="btn-primary w-full mt-6 py-3 text-sm">
                     Generate Missing Files
                   </button>
                </div>
              </div>

              {/* Right Column: Detailed Analysis */}
              <div className="col-span-12 lg:col-span-9 space-y-6">
                
                {/* Tip #3: Split by Engine */}
                <div className="glass-card p-8">
                  <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-100">
                    <Cpu className="text-primary" size={24} />
                    <h3 className="text-xl font-bold">Engine Visibility Protocol</h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <EngineCard name="GPT-4 (OpenAI)" {...getEngineStatus(result.aeo.robots_txt.content, 'GPTBot')} />
                    <EngineCard name="Claude 3" {...getEngineStatus(result.aeo.robots_txt.content, 'ClaudeBot')} />
                    <EngineCard name="Perplexity" {...getEngineStatus(result.aeo.robots_txt.content, 'PerplexityBot')} />
                    <EngineCard name="Google Gemini" {...getEngineStatus(result.aeo.robots_txt.content, 'Google-Extended')} />
                  </div>
                </div>

                {/* Advanced Signals */}
                <div className="glass-card p-8">
                  <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-100">
                    <Globe className="text-secondary" size={24} />
                    <h3 className="text-xl font-bold">Semantic Signals</h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(result.advanced_checks).map(([key, val]) => (
                      <div key={key} className="p-4 bg-white/50 rounded-xl border border-gray-100">
                        <div className="flex justify-between mb-2">
                          <span className="text-xs font-bold uppercase text-dim tracking-wider">{key.replace('_', ' ')}</span>
                          <span className={`text-xs font-bold ${val.status === 'Great' ? 'text-green-600' : 'text-orange-500'}`}>{val.status}</span>
                        </div>
                        <p className="text-sm font-medium">{val.detail}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

            </motion.div>
          )}
        </div>
      )}

      {/* Generate Modal */}
      {showGenerateModal && generatedFiles && (
        <div className="fixed inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={() => setShowGenerateModal(false)}>
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="glass-card max-w-4xl w-full p-8 max-h-[90vh] overflow-y-auto bg-white" onClick={(e) => e.stopPropagation()}>
             <h2 className="text-2xl font-bold mb-6">Generated Optimization Files</h2>
             <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {['llm_txt', 'ai_txt', 'robots_txt'].map((key) => (
                  <div key={key} className="p-4 border border-gray-200 rounded-xl">
                    <h3 className="font-bold mb-2">{key.replace('_', '.')}</h3>
                    <pre className="text-xs h-40 overflow-auto mb-3 bg-gray-900 text-gray-100 rounded p-2">
                      {generatedFiles[key as keyof GeneratedFiles] as string}
                    </pre>
                    <button onClick={() => downloadFile(key, generatedFiles[key as keyof GeneratedFiles] as string)} className="btn-secondary w-full py-2 text-xs">Download</button>
                  </div>
                ))}
             </div>
             <button onClick={() => setShowGenerateModal(false)} className="btn-primary w-full mt-8 py-3">Close</button>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default App;
