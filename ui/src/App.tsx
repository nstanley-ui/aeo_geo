import React, { useState } from 'react';
import { Search, Globe, Users, TrendingUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from 'recharts';

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
    platforms: Array<{
      name: string;
      score: number;
      status: string;
      tips: string[];
    }>;
  };
  optimized_files: {
    llm_txt: string;
    ai_txt: string;
    robots_txt: string;
  };
  advanced_checks: {
    [key: string]: { status: string; detail: string };
  };
}

interface CompetitorResult {
  target_domain: string;
  competitors: Array<{ name: string; domain: string; score: number }>;
}

interface GeneratedFiles {
  llm_txt: string;
  ai_txt: string;
  robots_txt: string;
  analysis: {
    pages_crawled: number;
    sections_found: string[];
    schema_types: string[];
  };
}

const App: React.FC = () => {
  const [domain, setDomain] = useState('ironhorse.io');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [competitors, setCompetitors] = useState<CompetitorResult | null>(null);
  const [compLoading, setCompLoading] = useState(false);
  const [showGradeModal, setShowGradeModal] = useState(false);
  const [selectedGrade, setSelectedGrade] = useState<{
    grade: string;
    fileType: string;
    criteria: any;
  } | null>(null);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [generatedFiles, setGeneratedFiles] = useState<GeneratedFiles | null>(null);
  const [generateLoading, setGenerateLoading] = useState(false);
  const [showCurrentModal, setShowCurrentModal] = useState(false);
  const [currentFileView, setCurrentFileView] = useState<{
    filename: string;
    content: string;
    domain: string;
  } | null>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setResult(null);
    setCompetitors(null);
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

  const handleCompetitors = async () => {
    setCompLoading(true);
    try {
      const resp = await fetch(`http://localhost:8000/competitors?domain=${domain}`);
      const data = await resp.json();
      setCompetitors(data);
    } catch (err) {
      console.error("Competitor check failed", err);
    } finally {
      setCompLoading(false);
    }
  };

  const downloadFile = (filename: string, content: string) => {
    const safeFilename = filename.endsWith('.txt') ? filename : `${filename}.txt`;
    const element = document.createElement("a");
    const file = new Blob([content], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = safeFilename;
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
    } catch (err) {
      console.error("File generation failed", err);
    } finally {
      setGenerateLoading(false);
    }
  };

  const openGradeModal = (grade: string, fileType: string, criteria: any) => {
    setSelectedGrade({ grade, fileType, criteria });
    setShowGradeModal(true);
  };

  const openCurrentFileModal = (filename: string, content: string, domain: string) => {
    setCurrentFileView({ filename, content, domain });
    setShowCurrentModal(true);
  };

  const chartData = result ? [
    { name: 'Overall', value: result.overall_score, fill: '#6366f1' },
  ] : [];

  return (
    <div className="min-h-screen p-4 lg:px-8 lg:py-4">
      <header className="mb-8 text-center max-w-6xl mx-auto">
        <motion.h1
          className="text-6xl lg:text-7xl font-black mb-2 vibrant-gradient-text tracking-tighter"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          MOJO AEO GEO CHECKER
        </motion.h1>
        <p className="text-dim text-xl lg:text-2xl font-medium">
          Is your Company even visible in the AI Agent economy?
        </p>
      </header>

      <div className="glass-card mb-8 max-w-6xl mx-auto flex flex-col md:flex-row items-center gap-6 p-6">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-6 top-6 text-dim" size={32} />
          <input
            type="text"
            className="pl-16 py-6 text-2xl w-full"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            placeholder="Enter your domain (e.g., ironhorse.io)"
          />
        </div>
        <button
          className="btn-primary w-full md:w-auto px-12 py-6 text-2xl"
          onClick={handleAnalyze}
          disabled={loading}
        >
          {loading ? 'Analyzing...' : 'Run Domain Audit'}
          <TrendingUp size={32} />
        </button>
      </div>

      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid-main max-w-[1700px] mx-auto"
          >
            {/* Main Mojo Score Section - Compact Left */}
            <div className="col-span-12 lg:col-span-2 glass-card flex flex-col items-center justify-center text-center p-6">
              <h3 className="text-xl font-black mb-4">Agent Mojo</h3>
              <div style={{ width: 140, height: 140 }} className="relative">
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart
                    innerRadius="85%"
                    outerRadius="100%"
                    data={chartData}
                    startAngle={180}
                    endAngle={-180}
                  >
                    <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
                    <RadialBar
                      background
                      dataKey="value"
                      cornerRadius={40}
                      fill="#6366f1"
                    />
                  </RadialBarChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-3xl font-black">{result.overall_score}</span>
                </div>
              </div>
              <p className="text-dim mt-4 text-[10px] uppercase tracking-tighter max-w-[120px]">
                Composite visibility visibility
              </p>

              <button
                onClick={handleCompetitors}
                disabled={compLoading}
                className="btn-secondary mt-6 py-2 px-4 text-[10px] flex items-center justify-center gap-1 font-bold w-full uppercase tracking-widest"
              >
                {compLoading ? 'Benchmarking...' : 'Benchmarking'}
                <Users size={12} />
              </button>
            </div>

            {/* AEO / GEO Detailed Analysis - Wider Right */}
            <div className="col-span-12 lg:col-span-10 glass-card p-6 lg:p-8">
              <div className="flex items-center gap-3 mb-6 text-primary border-b border-white/5 pb-4">
                <Globe size={24} />
                <h3 className="text-xl font-black">Agent-Facing Infrastructure</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <StatusItem
                  label="llm.txt"
                  grade={result.aeo.llm_txt.grade}
                  domain={domain}
                  filename="llm.txt"
                  currentContent={result.aeo.llm_txt.content}
                  optimizedContent={result.optimized_files.llm_txt}
                  onDownload={() => downloadFile('llm.txt', result.optimized_files.llm_txt)}
                  gradingCriteria={result.aeo.llm_txt.grading_criteria}
                  onLearnMore={() => openGradeModal(result.aeo.llm_txt.grade, 'llm.txt', result.aeo.llm_txt.grading_criteria)}
                  onViewCurrent={() => openCurrentFileModal('llm.txt', result.aeo.llm_txt.content || '', domain)}
                />
                <StatusItem
                  label="ai.txt"
                  grade={result.aeo.ai_txt.grade}
                  domain={domain}
                  filename="ai.txt"
                  currentContent={result.aeo.ai_txt.content}
                  optimizedContent={result.optimized_files.ai_txt}
                  onDownload={() => downloadFile('ai.txt', result.optimized_files.ai_txt)}
                  gradingCriteria={result.aeo.ai_txt.grading_criteria}
                  onLearnMore={() => openGradeModal(result.aeo.ai_txt.grade, 'ai.txt', result.aeo.ai_txt.grading_criteria)}
                  onViewCurrent={() => openCurrentFileModal('ai.txt', result.aeo.ai_txt.content || '', domain)}
                />
                <StatusItem
                  label="robots.txt"
                  grade={result.aeo.robots_txt.grade}
                  domain={domain}
                  filename="robots.txt"
                  currentContent={result.aeo.robots_txt.content}
                  optimizedContent={result.optimized_files.robots_txt}
                  onDownload={() => downloadFile('robots.txt', result.optimized_files.robots_txt)}
                  gradingCriteria={result.aeo.robots_txt.grading_criteria}
                  onLearnMore={() => openGradeModal(result.aeo.robots_txt.grade, 'robots.txt', result.aeo.robots_txt.grading_criteria)}
                  onViewCurrent={() => openCurrentFileModal('robots.txt', result.aeo.robots_txt.content || '', domain)}
                />
              </div>

              {/* Generate Files Button */}
              <div className="mb-6">
                <button
                  onClick={handleGenerateFiles}
                  disabled={generateLoading}
                  className="btn-primary w-full py-4 text-sm flex items-center justify-center gap-2 font-black uppercase tracking-widest"
                >
                  {generateLoading ? 'Analyzing Site & Generating Files...' : 'Generate Optimized AEO Files'}
                  <TrendingUp size={18} />
                </button>
              </div>

              {/* Advanced Content Checks */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(result.advanced_checks).map(([key, value]) => (
                  <div key={key} className="p-4 rounded-xl bg-white/5 border border-white/10 flex flex-col gap-1">
                    <span className="text-[10px] uppercase font-black tracking-widest text-dim">
                      {key.replace('_', ' ')}
                    </span>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold truncate pr-2">{value.detail}</span>
                      <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${value.status === 'Great' ? 'text-green-400 bg-green-400/10' :
                        value.status === 'Good' ? 'text-cyan-400 bg-cyan-400/10' :
                          'text-red-400 bg-red-400/10'
                        }`}>
                        {value.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Competitor Benchmarking (Conditional) */}
            {competitors && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="col-span-12 glass-card p-6 lg:p-10"
              >
                <div className="flex items-center gap-3 mb-8 text-accent">
                  <TrendingUp size={28} />
                  <h3 className="text-2xl font-black">Competitor Benchmarking</h3>
                </div>
                <div className="space-y-6">
                  {competitors.competitors.map((comp) => (
                    <div key={comp.domain} className="flex flex-col gap-2">
                      <div className="flex justify-between text-sm font-bold">
                        <span>{comp.name} ({comp.domain})</span>
                        <span className={comp.score > result.overall_score ? 'text-red-400' : 'text-green-400'}>
                          {comp.score}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${comp.score}%` }}
                          className={`h-full ${comp.score > result.overall_score ? 'bg-red-400' : 'bg-green-400'}`}
                        />
                      </div>
                    </div>
                  ))}
                  <div className="flex flex-col gap-2 pt-4 border-t border-white/10">
                    <div className="flex justify-between text-sm font-black text-primary">
                      <span>YOU ({domain})</span>
                      <span>{result.overall_score}%</span>
                    </div>
                    <div className="w-full bg-slate-800 h-4 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${result.overall_score}%` }}
                        className="h-full bg-primary"
                      />
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Social Visibility Grid */}
            <div className="col-span-12 glass-card">
              <div className="flex items-center gap-3 mb-6 text-accent">
                <Users size={24} />
                <h3 className="text-xl font-black">Entity & Social Favorability</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {result.social.platforms.map((plat) => (
                  <div key={plat.name} className="p-6 rounded-3xl bg-black/20 border border-white/5 flex flex-col">
                    <div className="flex justify-between items-end mb-4">
                      <span className="text-xl font-bold">{plat.name}</span>
                      <span className="text-3xl font-black text-accent">{plat.score}%</span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden mb-6">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${plat.score}%` }}
                        transition={{ duration: 1, ease: "easeOut" }}
                        className="bg-accent h-full shadow-[0_0_15px_rgba(6,182,212,0.5)]"
                      />
                    </div>
                    <div className="space-y-4">
                      <h5 className="text-[10px] font-black uppercase tracking-widest text-dim">Strategy</h5>
                      <ul className="text-sm text-dim space-y-1">
                        {plat.tips.map((tip, i) => (
                          <li key={i} className="flex gap-2">
                            <span className="text-accent">→</span>
                            {tip}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Grade Modal */}
      {showGradeModal && selectedGrade && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4" onClick={() => setShowGradeModal(false)}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card max-w-2xl w-full p-8"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-3xl font-black vibrant-gradient-text">Grade: {selectedGrade.grade}</h2>
              <button
                onClick={() => setShowGradeModal(false)}
                className="text-dim hover:text-white transition-colors text-2xl"
              >
                ×
              </button>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-black text-primary mb-2">File Type</h3>
                <p className="text-dim">{selectedGrade.fileType}</p>
              </div>

              {selectedGrade.criteria && Object.entries(selectedGrade.criteria).map(([grade, info]: [string, any]) => (
                <div key={grade} className={`p-4 rounded-xl ${grade === selectedGrade.grade ? 'bg-primary/10 border-2 border-primary' : 'bg-white/5 border border-white/10'}`}>
                  <h4 className="text-md font-black mb-2">{grade} ({info.score}/100)</h4>
                  <p className="text-sm text-dim mb-2"><strong>Criteria:</strong> {info.criteria}</p>
                  <p className="text-sm text-dim"><strong>Example:</strong> {info.example}</p>
                </div>
              ))}
            </div>

            <button
              onClick={() => setShowGradeModal(false)}
              className="btn-primary w-full mt-6 py-3"
            >
              Got it!
            </button>
          </motion.div>
        </div>
      )}

      {/* Generate Files Modal */}
      {showGenerateModal && generatedFiles && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4" onClick={() => setShowGenerateModal(false)}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card max-w-4xl w-full p-8 max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-3xl font-black vibrant-gradient-text">Generated AEO Files</h2>
              <button
                onClick={() => setShowGenerateModal(false)}
                className="text-dim hover:text-white transition-colors text-2xl"
              >
                ×
              </button>
            </div>

            {/* Crawl Summary */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-center">
                <div className="text-3xl font-black text-primary">{generatedFiles.analysis.pages_crawled}</div>
                <div className="text-xs text-dim uppercase tracking-widest mt-1">Pages Analyzed</div>
              </div>
              <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-center">
                <div className="text-3xl font-black text-secondary">{generatedFiles.analysis.sections_found.length}</div>
                <div className="text-xs text-dim uppercase tracking-widest mt-1">Sections Found</div>
              </div>
              <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-center">
                <div className="text-3xl font-black text-accent">{generatedFiles.analysis.schema_types.length}</div>
                <div className="text-xs text-dim uppercase tracking-widest mt-1">Schema Types</div>
              </div>
            </div>

            {/* File Previews */}
            <div className="space-y-4 mb-6">
              {['llm_txt', 'ai_txt', 'robots_txt'].map((fileKey) => (
                <div key={fileKey} className="p-4 rounded-xl bg-white/5 border border-white/10">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-black">{fileKey.replace('_', '.')}</h3>
                    <button
                      onClick={() => downloadFile(fileKey.replace('_', '.'), generatedFiles[fileKey as keyof typeof generatedFiles] as string)}
                      className="btn-secondary py-2 px-4 text-xs"
                    >
                      Download
                    </button>
                  </div>
                  <pre className="text-xs bg-black/40 p-4 rounded-lg overflow-x-auto max-h-48">
                    {(generatedFiles[fileKey as keyof typeof generatedFiles] as string) || ''}
                  </pre>
                </div>
              ))}
            </div>

            <button
              onClick={() => setShowGenerateModal(false)}
              className="btn-primary w-full py-3"
            >
              Close
            </button>
          </motion.div>
        </div>
      )}

      {/* Current File View Modal */}
      {showCurrentModal && currentFileView && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4" onClick={() => setShowCurrentModal(false)}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card max-w-4xl w-full p-8 max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-3xl font-black vibrant-gradient-text">Current: {currentFileView.filename}</h2>
              <button
                onClick={() => setShowCurrentModal(false)}
                className="text-dim hover:text-white transition-colors text-2xl"
              >
                ×
              </button>
            </div>

            <div className="mb-4">
              <p className="text-sm text-dim mb-2">
                Found at: <span className="text-primary">{currentFileView.domain}/{currentFileView.filename}</span>
              </p>
            </div>

            <div className="p-4 rounded-xl bg-white/5 border border-white/10">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-black">File Content</h3>
                <button
                  onClick={() => downloadFile(currentFileView.filename, currentFileView.content)}
                  className="btn-secondary py-2 px-4 text-xs"
                >
                  Download
                </button>
              </div>
              <pre className="text-xs bg-black/40 p-4 rounded-lg overflow-x-auto max-h-96 whitespace-pre-wrap">
                {currentFileView.content}
              </pre>
            </div>

            <button
              onClick={() => setShowCurrentModal(false)}
              className="btn-primary w-full mt-6 py-3"
            >
              Close
            </button>
          </motion.div>
        </div>
      )}
    </div>
  );
};

const StatusItem: React.FC<{
  label: string;
  grade: string;
  domain?: string;
  filename?: string;
  currentContent?: string | null;
  optimizedContent?: string;
  onDownload?: () => void;
  gradingCriteria?: any;
  onLearnMore?: () => void;
  onViewCurrent?: () => void;
}> = ({ label, grade, currentContent, onDownload, gradingCriteria, onLearnMore, onViewCurrent }) => {
  const [downloading, setDownloading] = useState(false);


  const handleDownload = async () => {
    setDownloading(true);
    await new Promise(r => setTimeout(r, 1500));
    if (onDownload) onDownload();
    setDownloading(false);
  };

  const getGradeColor = (g: string) => {
    switch (g) {
      case 'Great': return 'text-green-400 bg-green-400/10';
      case 'Good': return 'text-cyan-400 bg-cyan-400/10';
      case 'Average': return 'text-yellow-400 bg-yellow-400/10';
      case 'Poor': return 'text-red-400 bg-red-400/10';
      case 'Missing': return 'text-orange-400 bg-orange-400/10';
      default: return 'text-dim bg-white/5';
    }
  };

  return (
    <div className="flex flex-col gap-3 p-5 rounded-2xl bg-white/5 border border-white/10">
      <div className="flex items-center justify-between">
        <span className="text-sm font-black uppercase tracking-widest text-dim">{label}</span>
        <div className="flex items-center gap-2">
          <span className={`${getGradeColor(grade)} px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-widest`}>
            {grade}
          </span>
          {gradingCriteria && onLearnMore && (
            <button
              onClick={onLearnMore}
              className="text-[10px] text-primary hover:text-secondary transition-colors font-bold uppercase tracking-widest"
              title="Learn more about this grade"
            >
              ?
            </button>
          )}
        </div>
      </div>
      <div className="flex gap-2 mt-2 flex-wrap">
        {grade !== 'Missing' && currentContent && onViewCurrent && (
          <button
            onClick={onViewCurrent}
            className="flex-1 min-w-[100px] py-2 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center gap-2 text-[10px] font-black uppercase tracking-widest hover:bg-white/10 transition-colors"
          >
            See Current
          </button>
        )}
        {grade !== 'Great' && (
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="btn-secondary flex-1 min-w-[120px] py-2 text-[10px] flex items-center justify-center gap-2 font-black uppercase tracking-widest"
          >
            {downloading ? "Generating..." : "See Optimized"}
          </button>
        )}
      </div>
    </div>
  );
};

export default App;
