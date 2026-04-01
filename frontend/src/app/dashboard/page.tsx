"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { 
  FileText, 
  MessageSquare, 
  Briefcase, 
  Search, 
  RefreshCcw, 
  Upload, 
  LogOut,
  BrainCircuit,
  AlertCircle,
  Lightbulb,
  CheckCircle2,
  XCircle
} from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [resume, setResume] = useState("");
  const [transcript, setTranscript] = useState("");
  const [jobDesc, setJobDesc] = useState("");
  const [status, setStatus] = useState("Ready for analysis");
  const [result, setResult] = useState<any>(null);
  const [templates, setTemplates] = useState<any>({ candidates: [], jobs: [] });

  useEffect(() => {
    const auth = localStorage.getItem("user_auth");
    if (!auth) router.push("/login");

    // Load verified templates
    fetch("/verified_templates.json")
      .then(r => r.json())
      .then(data => setTemplates(data))
      .catch(err => console.error("Failed to load templates:", err));
  }, [router]);

  const randomizeApplicant = () => {
    if (templates.candidates.length === 0) return;
    const cand = templates.candidates[Math.floor(Math.random() * templates.candidates.length)];
    setResume(cand.resume);
    setTranscript(cand.transcript);
    setStatus(`Applicant Selected: ${cand.name} (${cand.role})`);
    setResult(null);
  };

  const randomizeJob = () => {
    const jobs = templates.jobs.length > 0 ? templates.jobs : 
                 templates.candidates.map((c: any) => ({ title: c.role, desc: c.job_desc }));
    if (jobs.length === 0) return;
    const job = jobs[Math.floor(Math.random() * jobs.length)];
    setJobDesc(job.desc || job.job_desc);
    setStatus(prev => prev.includes("Applicant") ? prev : `Job Selected: ${job.title}`);
    setResult(null);
  };

  const randomizeAll = () => {
    randomizeApplicant();
    randomizeJob();
    setStatus("Case Randomized: Ready for Analysis");
  };

  const handleLogout = () => {
    localStorage.removeItem("user_auth");
    router.push("/login");
  };

  const analyze = async () => {
    setLoading(true);
    setStatus("🧠 AI is processing...");
    
    try {
      // Use localhost to avoid IP mismatches
      const response = await fetch("http://localhost:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume,
          transcript,
          job_description: jobDesc
        })
      });

      const data = await response.json();
      setResult(data);
      setStatus("✅ Analysis Complete");
    } catch (error) {
      console.error(error);
      setStatus("❌ Server Connection Error. Is Flask running on port 5000?");
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setStatus(`Reading: ${file.name}...`);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:5000/upload_pdf", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (data.text) {
        setResume(data.text);
        setStatus(`✅ ${file.name} Parsed Successfully`);
      } else {
        setStatus(`❌ Error: ${data.error}`);
      }
    } catch (error) {
      setStatus("❌ PDF Service Unavailable. Is Flask running?");
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="glass border-b border-white/5 py-4 px-8 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-orange-500/20 rounded-xl">
            <BrainCircuit className="w-6 h-6 text-orange-400" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white/90">AI Recruitment <span className="text-orange-400">Intelligence</span></span>
        </div>
        <button 
          onClick={handleLogout}
          className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span className="text-sm font-medium">Logout</span>
        </button>
      </header>

      <main className="flex-1 p-8 max-w-7xl mx-auto w-full">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column: Inputs */}
          <div className="lg:col-span-2 space-y-6">
            <div className="glass rounded-3xl p-8 space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <FileText className="w-5 h-5 text-orange-400" />
                  Candidate Profile
                </h2>
                <div className="flex gap-2">
                   <button 
                      onClick={randomizeApplicant}
                      className="p-2 glass-hover rounded-lg text-slate-400 hover:text-white transition-all flex items-center gap-2 text-xs"
                    >
                      <RefreshCcw className="w-4 h-4" />
                      Shuffle
                   </button>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-widest ml-1">Resume Details</label>
                  <textarea 
                    value={resume}
                    onChange={(e) => setResume(e.target.value)}
                    placeholder="Paste candidate resume here..."
                    className="w-full bg-black/30 border border-white/5 rounded-2xl p-4 h-64 focus:ring-2 focus:ring-orange-500/50 outline-none resize-none transition-all"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-widest ml-1">Interview Transcript</label>
                  <textarea 
                    value={transcript}
                    onChange={(e) => setTranscript(e.target.value)}
                    placeholder="Paste interview dialogue here..."
                    className="w-full bg-black/30 border border-white/5 rounded-2xl p-4 h-64 focus:ring-2 focus:ring-orange-500/50 outline-none resize-none transition-all"
                  />
                </div>
              </div>
            </div>

            <div className="glass rounded-3xl p-8 space-y-4">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <Briefcase className="w-5 h-5 text-orange-400" />
                  Target Position
                </h2>
                <button 
                  onClick={randomizeJob}
                  className="p-2 glass-hover rounded-lg text-slate-400 hover:text-white transition-all flex items-center gap-2 text-xs"
                >
                    <RefreshCcw className="w-4 h-4" />
                    Shuffle
                </button>
              </div>
              <textarea 
                value={jobDesc}
                onChange={(e) => setJobDesc(e.target.value)}
                placeholder="Enter job description and requirements..."
                className="w-full bg-black/30 border border-white/5 rounded-2xl p-4 h-40 focus:ring-2 focus:ring-orange-500/50 outline-none resize-none transition-all"
              />
            </div>

            <div className="flex flex-wrap gap-4 pt-4">
              <input 
                  type="file" 
                  id="pdf_upload" 
                  accept=".pdf" 
                  className="hidden" 
                  onChange={handleFileUpload}
              />
              <button 
                onClick={analyze}
                disabled={loading || !resume || !jobDesc}
                className="flex-1 min-w-[200px] bg-orange-600 hover:bg-orange-500 disabled:bg-stone-800 disabled:text-stone-500 py-4 rounded-2xl font-bold text-lg shadow-xl shadow-orange-500/10 transition-all flex items-center justify-center gap-3"
              >
                {loading ? <RefreshCcw className="w-6 h-6 animate-spin" /> : <Search className="w-6 h-6" />}
                {loading ? "Processing Intelligence..." : "Begin Deep Analysis"}
              </button>
              
              <button 
                onClick={() => document.getElementById("pdf_upload")?.click()}
                className="px-6 py-4 glass hover:bg-white/5 rounded-2xl font-semibold transition-all flex items-center gap-2"
              >
                <Upload className="w-5 h-5 text-orange-400" />
                Upload PDF
              </button>

              <button 
                onClick={randomizeAll}
                className="px-6 py-4 glass border-emerald-500/20 hover:border-emerald-500/40 hover:bg-emerald-500/5 text-emerald-400 rounded-2xl font-semibold transition-all flex items-center gap-2"
              >
                🎲 Randomize Case
              </button>
            </div>
          </div>

          {/* Right Column: Results */}
          <div className="space-y-6">
            <div className="glass rounded-3xl p-8 h-full flex flex-col">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <BrainCircuit className="w-5 h-5 text-purple-400" />
                Evaluation Output
              </h2>

              {!result && (
                <div className="flex-1 flex flex-col items-center justify-center text-center space-y-4 text-slate-500">
                  <div className="p-6 bg-slate-900/50 rounded-full border border-white/5">
                    <BrainCircuit className="w-12 h-12 opacity-20" />
                  </div>
                  <p>Awaiting input data<br/><span className="text-xs uppercase tracking-widest mt-2">{status}</span></p>
                </div>
              )}

              <AnimatePresence>
                {result && (
                  <motion.div 
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="space-y-6 h-full flex flex-col"
                  >
                    <div className="flex flex-col items-center text-center py-6 border-b border-white/5 mb-6">
                       <span className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest mb-4 flex items-center gap-2 ${result.decision === 'SELECT' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
                          {result.decision === 'SELECT' ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                          {result.decision}
                       </span>
                       <div className="text-6xl font-black text-white">{Number(result.probability).toFixed(3)}%</div>
                       <p className="text-sm text-slate-400 mt-2">Selection Confidence Score</p>
                    </div>

                    <div className="space-y-2">
                       <div className="flex justify-between text-xs font-bold text-slate-500 uppercase tracking-widest pb-1">
                          <span>Matching Probability</span>
                          <span>{result.probability}%</span>
                       </div>
                       <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                          <motion.div 
                            initial={{ width: 0 }}
                            animate={{ width: `${result.probability}%` }}
                            className="h-full bg-gradient-to-r from-orange-500 to-red-500 shadow-[0_0_20px_rgba(249,115,22,0.5)]"
                          />
                       </div>
                    </div>

                    <div className="flex-1 mt-6 p-4 bg-orange-500/5 border border-orange-500/10 rounded-2xl overflow-hidden">
                       <h3 className="text-sm font-bold text-orange-400 flex items-center gap-2 mb-3">
                          <Lightbulb className="w-4 h-4" />
                          Recruiter's Advice
                       </h3>
                       <p className="text-sm text-slate-300 leading-relaxed italic">
                          "{result.advice}"
                       </p>
                    </div>

                    <p className="text-[10px] uppercase tracking-tighter text-slate-600 text-center mt-4">
                       Processed by RecruitmentIntelligence Engine v2.1
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

        </div>
      </main>

      <footer className="text-center py-6 text-slate-600 text-[10px] uppercase tracking-[0.2em]">
        © 2024 Neural Systems | Academic Presentation Tier
      </footer>
    </div>
  );
}
