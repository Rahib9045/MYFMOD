"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  Loader2,
  AlertCircle,
  Lightbulb,
  CheckCircle2,
  XCircle,
  ScanSearch,
  History,
  Trash2,
  BrainCircuit,
} from "lucide-react";
import AppHeader from "@/components/AppHeader";
import { useAuthGuard } from "@/lib/useAuth";
import {
  getCv,
  predict,
  uploadPdf,
  listAnalyses,
  getAnalysis,
  deleteAnalysis,
  type PredictResult,
  type Analysis,
} from "@/lib/api";

export default function SeekerAnalyzePage() {
  const { user, loading: booting } = useAuthGuard("seeker");

  const [cvText, setCvText] = useState("");
  const [jobDesc, setJobDesc] = useState("");
  const [result, setResult] = useState<PredictResult | null>(null);
  const [history, setHistory] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const refreshHistory = useCallback(async () => {
    try {
      setHistory(await listAnalyses(15));
    } catch {
      // Non-fatal: a 401 already redirects inside the API client.
    }
  }, []);

  useEffect(() => {
    if (!user) return;
    getCv()
      .then((d) => {
        if (d.cv_text) {
          setCvText(d.cv_text);
          setStatus("Your saved CV is loaded. Paste a job description to check it against.");
        }
      })
      .catch(() => undefined);
    refreshHistory();
  }, [user, refreshHistory]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setError("");
    setStatus(`Parsing ${file.name}...`);
    try {
      const data = await uploadPdf(file);
      setCvText(data.text);
      setStatus(`✅ ${data.filename} parsed`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not read that PDF.");
      setStatus("");
    } finally {
      e.target.value = "";
    }
  };

  const runAnalysis = async () => {
    if (!cvText.trim() || !jobDesc.trim()) {
      setError("Add your CV and a job description first.");
      return;
    }
    setLoading(true);
    setError("");
    setStatus("🧠 Analysing your CV against this role...");
    try {
      const data = await predict({ resume: cvText, transcript: "", job_description: jobDesc });
      setResult(data);
      setStatus("✅ Analysis complete — saved to your history");
      refreshHistory();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed.");
      setStatus("");
    } finally {
      setLoading(false);
    }
  };

  const loadPast = async (id: number) => {
    try {
      const full = await getAnalysis(id);
      setCvText(full.resume);
      setJobDesc(full.job_description);
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

  const removePast = async (id: number) => {
    try {
      await deleteAnalysis(id);
      setHistory((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete that analysis.");
    }
  };

  if (booting) {
    return (
      <div className="min-h-screen flex items-center justify-center text-slate-400 gap-3">
        <Loader2 className="w-6 h-6 animate-spin text-orange-400" />
        Loading...
      </div>
    );
  }

  const strong = result ? result.decision === "SELECT" : false;

  return (
    <div className="min-h-screen flex flex-col">
      <AppHeader user={user} />

      <main className="flex-1 p-8 max-w-6xl mx-auto w-full space-y-6">
        {error && (
          <div className="flex items-start gap-2 rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <ScanSearch className="w-6 h-6 text-orange-400" />
            CV Analysis
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Paste any job description — one from this site or anywhere else — and see how your CV
            measures up, with specific advice on improving it.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Inputs */}
          <div className="lg:col-span-2 space-y-5">
            <div className="glass rounded-3xl p-6 space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Your CV</label>
                <input type="file" id="cv_pdf" accept=".pdf" className="hidden" onChange={handleUpload} />
                <button
                  onClick={() => document.getElementById("cv_pdf")?.click()}
                  className="text-xs text-orange-400 hover:underline flex items-center gap-1"
                >
                  <Upload className="w-3.5 h-3.5" />
                  Upload PDF
                </button>
              </div>
              <textarea
                value={cvText}
                onChange={(e) => setCvText(e.target.value)}
                placeholder="Your CV text..."
                className="w-full bg-black/30 border border-white/5 rounded-2xl p-4 h-52 focus:ring-2 focus:ring-orange-500/50 outline-none resize-none text-sm leading-relaxed"
              />
            </div>

            <div className="glass rounded-3xl p-6 space-y-3">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">
                Job Description
              </label>
              <textarea
                value={jobDesc}
                onChange={(e) => setJobDesc(e.target.value)}
                placeholder="Paste the full job posting here — responsibilities, requirements, everything."
                className="w-full bg-black/30 border border-white/5 rounded-2xl p-4 h-44 focus:ring-2 focus:ring-orange-500/50 outline-none resize-none text-sm leading-relaxed"
              />
            </div>

            <button
              onClick={runAnalysis}
              disabled={loading || !cvText.trim() || !jobDesc.trim()}
              className="w-full bg-orange-600 hover:bg-orange-500 disabled:bg-stone-800 disabled:text-stone-500 py-4 rounded-2xl font-bold text-lg shadow-xl shadow-orange-500/10 transition-all flex items-center justify-center gap-3"
            >
              {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : <ScanSearch className="w-6 h-6" />}
              {loading ? "Analysing..." : "Analyse My CV"}
            </button>

            {status && <p className="text-xs uppercase tracking-widest text-slate-500">{status}</p>}
          </div>

          {/* Result */}
          <div className="glass rounded-3xl p-6 flex flex-col">
            <h2 className="text-lg font-semibold mb-5 flex items-center gap-2">
              <BrainCircuit className="w-5 h-5 text-purple-400" />
              Result
            </h2>

            {!result ? (
              <div className="flex-1 flex flex-col items-center justify-center text-center gap-4 text-slate-500 py-10">
                <div className="p-5 bg-slate-900/50 rounded-full border border-white/5">
                  <BrainCircuit className="w-10 h-10 opacity-20" />
                </div>
                <p className="text-sm">Your verdict and CV advice will appear here.</p>
              </div>
            ) : (
              <AnimatePresence>
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="space-y-5"
                >
                  <div className="flex flex-col items-center text-center pb-5 border-b border-white/5">
                    <span
                      className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest mb-3 flex items-center gap-2 ${
                        strong
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : "bg-red-500/10 text-red-400 border border-red-500/20"
                      }`}
                    >
                      {strong ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                      {strong ? "Strong fit" : "Weak fit"}
                    </span>
                    <div className="text-5xl font-black text-white">
                      {Number(result.probability).toFixed(1)}%
                    </div>
                    <p className="text-xs text-slate-500 mt-1.5">chance of being shortlisted</p>
                  </div>

                  <div className="p-4 bg-orange-500/5 border border-orange-500/10 rounded-2xl">
                    <h3 className="text-sm font-bold text-orange-400 flex items-center gap-2 mb-2">
                      <Lightbulb className="w-4 h-4" />
                      How to improve your CV
                    </h3>
                    <p className="text-sm text-slate-300 leading-relaxed italic">
                      &ldquo;{result.advice}&rdquo;
                    </p>
                  </div>

                  <p className="text-[10px] uppercase tracking-tighter text-slate-600 text-center">
                    Engine: {result.engine}
                  </p>
                </motion.div>
              </AnimatePresence>
            )}
          </div>
        </div>

        {/* History */}
        <div className="glass rounded-3xl p-6 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <History className="w-5 h-5 text-orange-400" />
            Past Analyses
            <span className="text-sm font-normal text-slate-500">({history.length})</span>
          </h2>

          {history.length === 0 ? (
            <p className="text-sm text-slate-500 py-6 text-center">
              Every analysis you run is saved here automatically.
            </p>
          ) : (
            <ul className="space-y-2 max-h-80 overflow-y-auto pr-1">
              {history.map((a) => (
                <li
                  key={a.id}
                  className="flex items-center gap-3 rounded-2xl border border-white/5 bg-black/20 p-4 hover:border-white/10 transition-all"
                >
                  <button onClick={() => loadPast(a.id)} className="flex-1 text-left min-w-0">
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                          a.decision === "SELECT"
                            ? "bg-emerald-500/10 text-emerald-400"
                            : "bg-red-500/10 text-red-400"
                        }`}
                      >
                        {a.decision === "SELECT" ? "Strong" : "Weak"}
                      </span>
                      <span className="text-sm font-semibold text-slate-200">
                        {(a.probability * 100).toFixed(1)}%
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
                    onClick={() => removePast(a.id)}
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
      </main>
    </div>
  );
}
