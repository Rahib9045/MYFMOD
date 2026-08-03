"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  FileText,
  Briefcase,
  Search,
  RefreshCcw,
  Upload,
  LogOut,
  BrainCircuit,
  AlertCircle,
  Lightbulb,
  CheckCircle2,
  XCircle,
  Save,
  FolderOpen,
  History,
  Trash2,
  Loader2,
} from "lucide-react";
import {
  me,
  logout,
  predict,
  uploadPdf,
  listPortfolios,
  createPortfolio,
  deletePortfolio,
  listAnalyses,
  getAnalysis,
  deleteAnalysis,
  type User,
  type Portfolio,
  type Analysis,
  type PredictResult,
} from "@/lib/api";

type Templates = {
  candidates: { name: string; role: string; resume: string; transcript: string; job_desc: string }[];
  jobs: { title: string; desc: string }[];
};

export default function DashboardPage() {
  const router = useRouter();

  const [user, setUser] = useState<User | null>(null);
  const [booting, setBooting] = useState(true);

  const [loading, setLoading] = useState(false);
  const [resume, setResume] = useState("");
  const [transcript, setTranscript] = useState("");
  const [jobDesc, setJobDesc] = useState("");
  const [status, setStatus] = useState("Ready for analysis");
  const [error, setError] = useState("");
  const [result, setResult] = useState<PredictResult | null>(null);
  const [templates, setTemplates] = useState<Templates>({ candidates: [], jobs: [] });

  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [activePortfolioId, setActivePortfolioId] = useState<number | null>(null);
  const [showSave, setShowSave] = useState(false);
  const [saveTitle, setSaveTitle] = useState("");
  const [saving, setSaving] = useState(false);

  const refreshSaved = useCallback(async () => {
    try {
      const [p, a] = await Promise.all([listPortfolios(), listAnalyses(20)]);
      setPortfolios(p);
      setAnalyses(a);
    } catch {
      // A 401 already redirects inside the API client; anything else is non-fatal here.
    }
  }, []);

  useEffect(() => {
    // Verify the token against the server rather than trusting localStorage.
    me()
      .then((u) => {
        setUser(u);
        setBooting(false);
        refreshSaved();
      })
      .catch(() => router.push("/login"));

    fetch("/verified_templates.json")
      .then((r) => r.json())
      .then((data) => setTemplates(data))
      .catch(() => undefined);
  }, [router, refreshSaved]);

  const randomizeApplicant = () => {
    if (templates.candidates.length === 0) return;
    const cand = templates.candidates[Math.floor(Math.random() * templates.candidates.length)];
    setResume(cand.resume);
    setTranscript(cand.transcript);
    setStatus(`Applicant Selected: ${cand.name} (${cand.role})`);
    setResult(null);
    setActivePortfolioId(null);
  };

  const randomizeJob = () => {
    const jobs =
      templates.jobs.length > 0
        ? templates.jobs
        : templates.candidates.map((c) => ({ title: c.role, desc: c.job_desc }));
    if (jobs.length === 0) return;
    const job = jobs[Math.floor(Math.random() * jobs.length)];
    setJobDesc(job.desc);
    setStatus((prev) => (prev.includes("Applicant") ? prev : `Job Selected: ${job.title}`));
    setResult(null);
  };

  const randomizeAll = () => {
    randomizeApplicant();
    randomizeJob();
    setStatus("Case Randomized: Ready for Analysis");
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const analyze = async () => {
    setLoading(true);
    setError("");
    setStatus("🧠 AI is processing...");
    try {
      const data = await predict({
        resume,
        transcript,
        job_description: jobDesc,
        portfolio_id: activePortfolioId,
      });
      setResult(data);
      setStatus("✅ Analysis Complete — saved to your history");
      refreshSaved();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed.");
      setStatus("❌ Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setStatus(`Reading: ${file.name}...`);
    setError("");
    try {
      const text = await uploadPdf(file);
      setResume(text);
      setStatus(`✅ ${file.name} Parsed Successfully`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "PDF parsing failed.");
      setStatus("❌ Could not read that PDF");
    } finally {
      e.target.value = "";
    }
  };

  const handleSavePortfolio = async () => {
    if (!saveTitle.trim()) return;
    setSaving(true);
    setError("");
    try {
      const portfolio = await createPortfolio({
        title: saveTitle.trim(),
        resume,
        transcript,
        job_description: jobDesc,
      });
      setPortfolios((prev) => [portfolio, ...prev]);
      setActivePortfolioId(portfolio.id);
      setShowSave(false);
      setSaveTitle("");
      setStatus(`💾 Saved portfolio "${portfolio.title}"`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save portfolio.");
    } finally {
      setSaving(false);
    }
  };

  const handleLoadPortfolio = (portfolio: Portfolio) => {
    setResume(portfolio.resume);
    setTranscript(portfolio.transcript);
    setJobDesc(portfolio.job_description);
    setActivePortfolioId(portfolio.id);
    setResult(null);
    setStatus(`📂 Loaded "${portfolio.title}"`);
  };

  const handleDeletePortfolio = async (id: number) => {
    try {
      await deletePortfolio(id);
      setPortfolios((prev) => prev.filter((p) => p.id !== id));
      if (activePortfolioId === id) setActivePortfolioId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete portfolio.");
    }
  };

  const handleLoadAnalysis = async (id: number) => {
    try {
      const full = await getAnalysis(id);
      setResume(full.resume);
      setTranscript(full.transcript);
      setJobDesc(full.job_description);
      setActivePortfolioId(full.portfolio_id);
      setResult({
        analysis_id: full.id,
        probability: full.probability * 100,
        decision: full.decision,
        advice: full.advice,
        engine: full.engine,
        message: "Loaded from history.",
      });
      setStatus("🕘 Loaded a past analysis");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load that analysis.");
    }
  };

  const handleDeleteAnalysis = async (id: number) => {
    try {
      await deleteAnalysis(id);
      setAnalyses((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete analysis.");
    }
  };

  if (booting) {
    return (
      <div className="min-h-screen flex items-center justify-center text-slate-400 gap-3">
        <Loader2 className="w-6 h-6 animate-spin text-orange-400" />
        Loading your workspace...
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="glass border-b border-white/5 py-4 px-8 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-orange-500/20 rounded-xl">
            <BrainCircuit className="w-6 h-6 text-orange-400" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white/90">
            AI Recruitment <span className="text-orange-400">Intelligence</span>
          </span>
        </div>
        <div className="flex items-center gap-6">
          <span className="text-sm text-slate-400 hidden sm:block">
            Signed in as <span className="text-slate-200 font-medium">{user?.name}</span>
          </span>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span className="text-sm font-medium">Logout</span>
          </button>
        </div>
      </header>

      <main className="flex-1 p-8 max-w-7xl mx-auto w-full space-y-8">
        {error && (
          <div className="flex items-start gap-2 rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Inputs */}
          <div className="lg:col-span-2 space-y-6">
            <div className="glass rounded-3xl p-8 space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <FileText className="w-5 h-5 text-orange-400" />
                  Candidate Profile
                </h2>
                <button
                  onClick={randomizeApplicant}
                  className="p-2 glass-hover rounded-lg text-slate-400 hover:text-white transition-all flex items-center gap-2 text-xs"
                >
                  <RefreshCcw className="w-4 h-4" />
                  Shuffle
                </button>
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
              <input type="file" id="pdf_upload" accept=".pdf" className="hidden" onChange={handleFileUpload} />
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
                onClick={() => setShowSave((s) => !s)}
                disabled={!resume && !jobDesc}
                className="px-6 py-4 glass hover:bg-white/5 disabled:opacity-40 rounded-2xl font-semibold transition-all flex items-center gap-2"
              >
                <Save className="w-5 h-5 text-orange-400" />
                Save Portfolio
              </button>

              <button
                onClick={randomizeAll}
                className="px-6 py-4 glass border-emerald-500/20 hover:border-emerald-500/40 hover:bg-emerald-500/5 text-emerald-400 rounded-2xl font-semibold transition-all flex items-center gap-2"
              >
                🎲 Randomize Case
              </button>
            </div>

            <AnimatePresence>
              {showSave && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="glass rounded-2xl p-4 flex flex-wrap gap-3 items-center overflow-hidden"
                >
                  <input
                    autoFocus
                    value={saveTitle}
                    onChange={(e) => setSaveTitle(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSavePortfolio()}
                    placeholder="Name this portfolio, e.g. 'Kara Harvey — Data Analyst'"
                    className="flex-1 min-w-[240px] bg-black/30 border border-white/5 rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-orange-500/50 outline-none"
                  />
                  <button
                    onClick={handleSavePortfolio}
                    disabled={saving || !saveTitle.trim()}
                    className="bg-orange-600 hover:bg-orange-500 disabled:opacity-40 px-5 py-2.5 rounded-xl font-semibold flex items-center gap-2"
                  >
                    {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                    Save
                  </button>
                  <button
                    onClick={() => setShowSave(false)}
                    className="text-slate-400 hover:text-white px-3 py-2.5 text-sm"
                  >
                    Cancel
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
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
                  <p>
                    Awaiting input data
                    <br />
                    <span className="text-xs uppercase tracking-widest mt-2">{status}</span>
                  </p>
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
                      <span
                        className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest mb-4 flex items-center gap-2 ${
                          result.decision === "SELECT"
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            : "bg-red-500/10 text-red-400 border border-red-500/20"
                        }`}
                      >
                        {result.decision === "SELECT" ? (
                          <CheckCircle2 className="w-3.5 h-3.5" />
                        ) : (
                          <XCircle className="w-3.5 h-3.5" />
                        )}
                        {result.decision}
                      </span>
                      <div className="text-6xl font-black text-white">{Number(result.probability).toFixed(3)}%</div>
                      <p className="text-sm text-slate-400 mt-2">Selection Confidence Score</p>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-xs font-bold text-slate-500 uppercase tracking-widest pb-1">
                        <span>Matching Probability</span>
                        <span>{Number(result.probability).toFixed(2)}%</span>
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
                        Recruiter&apos;s Advice
                      </h3>
                      <p className="text-sm text-slate-300 leading-relaxed italic">&ldquo;{result.advice}&rdquo;</p>
                    </div>

                    <p className="text-[10px] uppercase tracking-tighter text-slate-600 text-center mt-4">
                      Engine: {result.engine}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>

        {/* Saved data */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="glass rounded-3xl p-8 space-y-4">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <FolderOpen className="w-5 h-5 text-orange-400" />
              Saved Portfolios
              <span className="text-sm font-normal text-slate-500">({portfolios.length})</span>
            </h2>

            {portfolios.length === 0 ? (
              <p className="text-sm text-slate-500 py-6 text-center">
                Nothing saved yet. Fill in a candidate and hit <span className="text-slate-300">Save Portfolio</span>.
              </p>
            ) : (
              <ul className="space-y-2 max-h-80 overflow-y-auto pr-1">
                {portfolios.map((p) => (
                  <li
                    key={p.id}
                    className={`flex items-center gap-3 rounded-2xl border p-4 transition-all ${
                      activePortfolioId === p.id
                        ? "border-orange-500/40 bg-orange-500/5"
                        : "border-white/5 bg-black/20 hover:border-white/10"
                    }`}
                  >
                    <button onClick={() => handleLoadPortfolio(p)} className="flex-1 text-left">
                      <div className="font-medium text-slate-200">{p.title}</div>
                      <div className="text-xs text-slate-500 mt-0.5">
                        {p.updated_at ? new Date(p.updated_at).toLocaleString() : ""}
                      </div>
                    </button>
                    <button
                      onClick={() => handleDeletePortfolio(p.id)}
                      className="p-2 text-slate-600 hover:text-red-400 transition-colors"
                      aria-label={`Delete ${p.title}`}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="glass rounded-3xl p-8 space-y-4">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <History className="w-5 h-5 text-orange-400" />
              Analysis History
              <span className="text-sm font-normal text-slate-500">({analyses.length})</span>
            </h2>

            {analyses.length === 0 ? (
              <p className="text-sm text-slate-500 py-6 text-center">
                Every analysis you run is saved here automatically.
              </p>
            ) : (
              <ul className="space-y-2 max-h-80 overflow-y-auto pr-1">
                {analyses.map((a) => (
                  <li
                    key={a.id}
                    className="flex items-center gap-3 rounded-2xl border border-white/5 bg-black/20 p-4 hover:border-white/10 transition-all"
                  >
                    <button onClick={() => handleLoadAnalysis(a.id)} className="flex-1 text-left min-w-0">
                      <div className="flex items-center gap-2">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                            a.decision === "SELECT"
                              ? "bg-emerald-500/10 text-emerald-400"
                              : "bg-red-500/10 text-red-400"
                          }`}
                        >
                          {a.decision}
                        </span>
                        <span className="text-sm font-semibold text-slate-200">
                          {(a.probability * 100).toFixed(2)}%
                        </span>
                      </div>
                      <div className="text-xs text-slate-500 mt-1 truncate">
                        {a.job_preview || "No job description"}
                      </div>
                      <div className="text-[10px] text-slate-600 mt-0.5">
                        {a.created_at ? new Date(a.created_at).toLocaleString() : ""}
                      </div>
                    </button>
                    <button
                      onClick={() => handleDeleteAnalysis(a.id)}
                      className="p-2 text-slate-600 hover:text-red-400 transition-colors"
                      aria-label="Delete analysis"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </main>

      <footer className="text-center py-6 text-slate-600 text-[10px] uppercase tracking-[0.2em]">
        © 2024 Neural Systems | Academic Presentation Tier
      </footer>
    </div>
  );
}
