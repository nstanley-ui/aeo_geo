import React, { useState } from 'react';
import { Search, Globe, TrendingUp, CheckCircle, XCircle, AlertTriangle, Cpu, FileText, ArrowRight, ShieldCheck, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from 'recharts';

// --- Types ---
interface AnalysisResult {
  domain: string;
  overall_score: number;
  aeo: {
    aeo_score: number;
    llm_txt: { exists: boolean; content: string | null; grade: string };
    ai_txt: { exists: boolean; content: string | null; grade: string };
    robots_txt: { exists: boolean; content: string | null; ai_friendly: boolean; grade: string };
  };
  optimized_files: { llm_txt: string; ai_txt: string; robots_txt: string };
  advanced_checks: { [key: string]: { status: string; detail: string } };
}

interface GeneratedFiles {
  llm_txt: string; ai_txt: string; robots_txt: string;
}

// --- Helper Components ---

// Tip #3: Compact Engine Status Card
const EngineCard: React.FC<{ name: string; status: 'Allowed' | 'Blocked' | 'Unknown'; detail: string }> = ({ name, status, detail }) => {
  const badgeClass = status === 'Allowed' ? 'badge-success' : status === 'Blocked' ? 'badge-error' : 'badge-neutral';
  const icon = status === 'Allowed' ? <CheckCircle size={14} /> : status === 'Blocked' ? <XCircle size={14} /> : <AlertTriangle size={14} />;
  
  return (
    <div className="p-3 rounded-lg bg-white/40 border border-stone-200 flex flex-col justify-between h-full hover:bg-white/60 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <span className="font-bold text-xs text-stone-700">{name}</span>
        <div className={`${badgeClass} p-1 rounded-full`}>{icon}</div>
      </div>
      <span className="text-[10px] font-medium text-stone-500 uppercase tracking-wide">{detail}</span>
    </div>
  );
};

// --- Main App Component ---
const App: React.FC = () => {
  const [domain, setDomain] = useState('ironhorse.io');
  const [loading, setLoading] = useState(false);
  
  // Tip #1: Entity Confirmation State
  const [step, setStep] = useState<'input' | 'confirm' | 'results'>('input');
  const [entityData, setEntityData] = useState<{ name: string; type: string }>({ name: '', type: 'Organization' });

  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [generatedFiles, setGeneratedFiles] = useState<GeneratedFiles | null>(null);
  const [generateLoading, setGenerateLoading] = useState(false);

  // 1. Initial Fetch
  const handleInitialCheck = () => {
    if (!domain) return;
    const detectedName = domain.split('.')[0].charAt(0).toUpperCase() + domain.split('.')[0].slice(1);
    setEntityData({ name: detectedName, type: 'Organization' });
    setStep('confirm');
  };

  // 2. Confirm Entity & Analyze
  const handleConfirmAndAnalyze = async () => {
    setLoading(true);
    setStep('results');
    setResult(null);
    try {
      const resp = await fetch(`http://localhost:8000/analyze?domain=${domain}`);
      const data = await resp.json();
      setResult(data);
    } catch (err) { console.error(err); } 
    finally { setLoading(false); }
  };

  const getEngineStatus = (content: string | null, botName: string) => {
    if (!content) return { status: 'Unknown', detail: 'Missing robots.txt' } as const;
    if (content.includes(`User-agent: ${botName}`) && content.includes("Disallow: /")) return { status: 'Blocked', detail: 'Blocked' } as const;
    if (content.includes(`User-agent: ${botName}`) && content.includes("Allow: /")) return { status: 'Allowed', detail: 'Explicit Allow' } as const;
    return { status: 'Allowed', detail: 'Implicit Allow' } as const;
  };

  const downloadFile = (filename: string, content: string) => {
    const element = document.createElement("a");
    const file = new Blob([content], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = filename;
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

  const chartData = result ? [{ name: 'Overall', value: result.overall_score, fill: '#ea580c' }] : [];

  return (
    <div className="min-h-screen p-4 flex flex-col items-center pt-10">
      
      {/* Header - Compact & Editorial */}
      <header className={`text-center transition-all duration-500 ${step === 'results' ? 'mb-6' : 'mb-12 scale-110'}`}>
        <h1 className="text-3xl font-black mb-1 vibrant-gradient-text tracking-tight uppercase">Mojo AEO Checker</h1>
        <p className="text-stone-500 text-sm font-medium tracking-wide">Agent Economy Optimization Intelligence</p>
      </header>

      {/* STEP 1: Input */}
      {step === 'input' && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card w-full max-w-lg p-6 shadow-xl">
          <div className="relative mb-4">
            <Search className="absolute left-4 top-3.5 text-stone-400" size={18} />
            <input
              type="text"
              className="pl-11 py-3 w-full text-base font-medium"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              placeholder="Enter domain (e.g. ironhorse.io)"
              onKeyDown={(e) => e.key === 'Enter' && handleInitialCheck()}
            />
          </div>
          <button onClick={handleInitialCheck} className="btn-primary w-full py-3 text-sm flex items-center justify-center gap-2">
            Start Audit <ArrowRight size={16} />
          </button>
        </motion.div>
      )}

      {/* STEP 2: Tip #1 Entity Confirmation */}
      {step === 'confirm' && (
        <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="glass-card w-full max-w-xl p-6 border-t-4 border-t-primary">
          <div className="flex items-center gap-3 mb-4 text-stone-700">
            <ShieldCheck className="text-primary" size={24} />
            <h2 className="text-lg font-bold">Verify Identity</h2>
          </div>
          <p className="text-stone-500 text-sm mb-6 bg-orange-50 p-3 rounded-lg border border-orange-100">
            <strong>Why this matters:</strong> Accurate scoring requires establishing the correct semantic entity before analysis begins.
          </p>
          
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-[10px] font-bold uppercase text-stone-400 mb-1">Brand Name</label>
              <input type="text" value={entityData.name} onChange={(e) => setEntityData({...entityData, name: e.target.value})} className="w-full p-2.5 font-bold text-stone-700" />
            </div>
            <div>
              <label className="block text-[10px] font-bold uppercase text-stone-400 mb-1">Entity Type</label>
              <select value={entityData.type} onChange={(e) => setEntityData({...entityData, type: e.target.value})} className="w-full p-2.5">
                <option>Organization</option><option>Product</option><option>Person</option>
              </select>
            </div>
          </div>

          <div className="flex gap-3">
            <button onClick={() => setStep('input')} className="btn-secondary flex-1 py-2.5">Back</button>
            <button onClick={handleConfirmAndAnalyze} className="btn-primary flex-[2] py-2.5 flex justify-center items-center gap-2">
              Confirm & Run Analysis <TrendingUp size={16} />
            </button>
          </div>
        </motion.div>
      )}

      {/* STEP 3: Results Dashboard - Compact Layout */}
      {step === 'results' && (
        <div className="w-full max-w-[1200px]">
          {loading ? (
            <div className="glass-card p-12 text-center max-w-lg mx-auto">
              <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-3"/>
              <p className="text-sm font-medium text-stone-500 animate-pulse">Analyzing semantic protocols...</p>
            </div>
          ) : result && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="grid grid-cols-12 gap-4">
              
              {/* Left Sidebar: Score & Files */}
              <div className="col-span-12 lg:col-span-3 space-y-4">
                <div className="glass-card p-5 flex flex-col items-center text-center">
                  <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest mb-2">Mojo Score</span>
                  <div className="relative w-32 h-32 mb-2">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadialBarChart innerRadius="80%" outerRadius="100%" data={chartData} startAngle={180} endAngle={-180}>
                        <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
                        <RadialBar background dataKey="value" cornerRadius={20} fill="#ea580c" />
                      </RadialBarChart>
                    </ResponsiveContainer>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-3xl font-black text-primary">{result.overall_score}</span>
                    </div>
                  </div>
                </div>

                <div className="glass-card p-4">
                   <h4 className="font-bold text-xs mb-3 flex items-center gap-2 text-stone-600"><FileText size={14}/> Core Files</h4>
                   <div className="space-y-2">
                     {[
                       {name: 'llm.txt', exists: result.aeo.llm_txt.exists, grade: result.aeo.llm_txt.grade},
                       {name: 'ai.txt', exists: result.aeo.ai_txt.exists, grade: result.aeo.ai_txt.grade},
                       {name: 'robots.txt', exists: result.aeo.robots_txt.exists, grade: result.aeo.robots_txt.grade},
                     ].map(f => (
                       <div key={f.name} className="flex justify-between items-center p-2.5 bg-white/40 rounded border border-stone-100">
                         <span className="font-medium text-xs text-stone-700">{f.name}</span>
                         <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${f.exists ? 'badge-success' : 'badge-error'}`}>
                           {f.exists ? f.grade : 'Missing'}
                         </span>
                       </div>
                     ))}
                   </div>
                   <button onClick={handleGenerateFiles} disabled={generateLoading} className="btn-secondary w-full mt-3 py-2 text-xs">
                     {generateLoading ? 'Generating...' : 'Generate Assets'}
                   </button>
                </div>
              </div>

              {/* Main Content Area */}
              <div className="col-span-12 lg:col-span-9 space-y-4">
                
                {/* Tip #3: Engine Split (Compact Grid) */}
                <div className="glass-card p-5">
                  <div className="flex items-center gap-2 mb-4 pb-2 border-b border-stone-100">
                    <Cpu className="text-primary" size={18} />
                    <h3 className="text-sm font-bold uppercase tracking-wide text-stone-600">Engine Visibility Protocol</h3>
                  </div>
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                    <EngineCard name="GPT-4" {...getEngineStatus(result.aeo.robots_txt.content, 'GPTBot')} />
                    <EngineCard name="Claude 3" {...getEngineStatus(result.aeo.robots_txt.content, 'ClaudeBot')} />
                    <EngineCard name="Perplexity" {...getEngineStatus(result.aeo.robots_txt.content, 'PerplexityBot')} />
                    <EngineCard name="Google Gemini" {...getEngineStatus(result.aeo.robots_txt.content, 'Google-Extended')} />
                  </div>
                </div>

                {/* Advanced Signals List */}
                <div className="glass-card p-5">
                  <div className="flex items-center gap-2 mb-4 pb-2 border-b border-stone-100">
                    <Globe className="text-primary" size={18} />
                    <h3 className="text-sm font-bold uppercase tracking-wide text-stone-600">Semantic Signals</h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {Object.entries(result.advanced_checks).map(([key, val]) => (
                      <div key={key} className="p-3 bg-white/40 rounded border border-stone-100 flex flex-col gap-1">
                         <div className="flex justify-between items-center">
                            <span className="text-[10px] font-bold uppercase text-stone-400 tracking-wider">{key.replace('_', ' ')}</span>
                            <span className={`text-[10px] font-bold px-1.5 rounded-sm ${val.status === 'Great' ? 'badge-success' : 'badge-warning'}`}>{val.status}</span>
                         </div>
                         <p className="text-xs font-medium text-stone-600 leading-tight">{val.detail}</p>
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
        <div className="fixed inset-0 bg-stone-900/20 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={() => setShowGenerateModal(false)}>
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="glass-card w-full max-w-3xl p-6 bg-white shadow-2xl" onClick={(e) => e.stopPropagation()}>
             <div className="flex justify-between items-center mb-6">
               <h2 className="text-lg font-bold text-stone-800">Generated Optimization Assets</h2>
               <button onClick={() => setShowGenerateModal(false)} className="text-stone-400 hover:text-stone-600"><XCircle size={20}/></button>
             </div>
             <div className="grid grid-cols-3 gap-4 mb-6">
                {['llm_txt', 'ai_txt', 'robots_txt'].map((key) => (
                  <div key={key} className="p-3 border border-stone-200 rounded-lg bg-stone-50">
                    <h3 className="font-bold text-xs mb-2 text-stone-600 uppercase">{key.replace('_', '.')}</h3>
                    <div className="text-[10px] h-32 overflow-hidden relative mb-2 font-mono text-stone-500 bg-white p-2 border border-stone-100 rounded">
                      {generatedFiles[key as keyof GeneratedFiles] as string}
                      <div className="absolute bottom-0 left-0 w-full h-8 bg-gradient-to-t from-white to-transparent"/>
                    </div>
                    <button onClick={() => downloadFile(key.replace('_', '.'), generatedFiles[key as keyof GeneratedFiles] as string)} className="btn-secondary w-full py-1.5 text-xs">Download</button>
                  </div>
                ))}
             </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default App;
