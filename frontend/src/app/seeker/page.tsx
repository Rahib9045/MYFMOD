"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  Search,
  Loader2,
  AlertCircle,
  MapPin,
  Clock,
  Sparkles,
  CheckCircle2,
  Lightbulb,
  Send,
  FileUser,
  Save,
} from "lucide-react";
import AppHeader from "@/components/AppHeader";
import { useAuthGuard } from "@/lib/useAuth";
import {
  getCv,
  saveCv,
  matchJobs,
  analyzeAgainstJob,
  applyToJob,
  uploadPdf,
  type JobMatch,
} from "@/lib/api";

type Deep = { probability: number; decision: "SELECT" | "REJECT"; advice: string; engine: string };

export default function SeekerPage() {
  const { user, setUser, loading: booting } = useAuthGuard("seeker");

  const [cvText, setCvText] = useState("");
  const [cvFilename, setCvFilename] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const [matches, setMatches] = useState<JobMatch[] | null>(null);
  const [totalOpen, setTotalOpen] = useState(0);
  const [searching, setSearching] = useState(false);
  const [savingCv, setSavingCv] = useState(false);

  const [openId, setOpenId] = useState<number | null>(null);
  const [deep, setDeep] = useState<Record<number, Deep>>({});
  const [analyzing, setAnalyzing] = useState<number | null>(null);
  const [applying, setApplying] = useState<number | null>(null);
  const [coverNote, setCoverNote] = useState("");

  useEffect(() => {
    if (!user) return;
    getCv()
      .then((d) => {
        setCvText(d.cv_text);
        setCvFilename(d.cv_filename);
        if (d.cv_text) setStatus("Saved CV loaded — search whenever you're ready.");
      })
      .catch(() => undefined);
  }, [user]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setError("");
    setStatus(`Parsing ${file.name}...`);
    try {
      const data = await uploadPdf(file);
      setCvText(data.text);
      setCvFilename(data.filename);
      setStatus(`✅ ${data.filename} parsed — ${data.text.length.toLocaleString()} characters`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not read that PDF.");
      setStatus("");
    } finally {
      e.target.value = "";
    }
  };

  const handleSaveCv = async () => {
    if (!cvText.trim()) return;
    setSavingCv(true);
    setError("");
    try {
      const updated = await saveCv(cvText, cvFilename);
      setUser(updated);
      setStatus("💾 CV saved to your profile.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save your CV.");
    } finally {
      setSavingCv(false);
    }
  };

  const findJobs = async () => {
    if (!cvText.trim()) {
      setError("Add your CV first — upload a PDF or paste the text.");
      return;
    }
    setSearching(true);
    setError("");
    setStatus("🔎 Scoring your CV against every open vacancy...");
    try {
      const data = await matchJobs({ cv_text: cvText, save_cv: true });
      setMatches(data.matches);
      setTotalOpen(data.total_open_jobs);
      setStatus(
        data.total_open_jobs === 0
          ? "No vacancies have been posted yet."
          : `Ranked ${data.matches.length} of ${data.total_open_jobs} open vacancies.`
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Matching failed.");
      setStatus("");
    } finally {
      setSearching(false);
    }
  };

  const runDeepDive = async (jobId: number) => {
    setAnalyzing(jobId);
    setError("");
    try {
      const result = await analyzeAgainstJob(jobId, cvText);
      setDeep((prev) => ({ ...prev, [jobId]: result }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed.");
    } finally {
      setAnalyzing(null);
    }
  };

  const handleApply = async (jobId: number) => {
    setApplying(jobId);
    setError("");
    try {
      await applyToJob(jobId, { cover_note: coverNote });
      setMatches((prev) => prev?.map((m) => (m.id === jobId ? { ...m, already_applied: true } : m)) ?? null);
      setCoverNote("");
      setStatus("✅ Application sent.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not apply.");
    } finally {
      setApplying(null);
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
      <AppHeader user={user} />

      <main className="flex-1 p-8 max-w-6xl mx-auto w-full space-y-6">
        {error && (
          <div className="flex items-start gap-2 rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* CV input */}
        <div className="glass rounded-3xl p-8 space-y-5">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <FileUser className="w-6 h-6 text-orange-400" />
                Your CV
              </h1>
              <p className="text-sm text-slate-500 mt-1">
                Drop in your CV and we&apos;ll rank every open vacancy against it.
              </p>
            </div>
            {cvFilename && (
              <span className="text-xs text-slate-500 bg-white/5 px-3 py-1.5 rounded-lg">{cvFilename}</span>
            )}
          </div>

          <textarea
            value={cvText}
            onChange={(e) => setCvText(e.target.value)}
            placeholder="Paste your CV here, or upload a PDF below..."
            className="w-full bg-black/30 border border-white/5 rounded-2xl p-4 h-56 focus:ring-2 focus:ring-orange-500/50 outline-none resize-none transition-all text-sm leading-relaxed"
          />

          <div className="flex flex-wrap gap-3 items-center">
            <input type="file" id="cv_upload" accept=".pdf" className="hidden" onChange={handleUpload} />
            <button
              onClick={() => document.getElementById("cv_upload")?.click()}
              className="px-5 py-3 glass hover:bg-white/5 rounded-2xl font-semibold flex items-center gap-2 transition-all"
            >
              <Upload className="w-5 h-5 text-orange-400" />
              Upload PDF
            </button>

            <button
              onClick={handleSaveCv}
              disabled={savingCv || !cvText.trim()}
              className="px-5 py-3 glass hover:bg-white/5 disabled:opacity-40 rounded-2xl font-semibold flex items-center gap-2 transition-all"
            >
              {savingCv ? <Loader2 className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5 text-orange-400" />}
              Save CV
            </button>

            <button
              onClick={findJobs}
              disabled={searching || !cvText.trim()}
              className="flex-1 min-w-[220px] bg-orange-600 hover:bg-orange-500 disabled:bg-stone-800 disabled:text-stone-500 py-3 rounded-2xl font-bold text-lg shadow-xl shadow-orange-500/10 transition-all flex items-center justify-center gap-3"
            >
              {searching ? <Loader2 className="w-6 h-6 animate-spin" /> : <Search className="w-6 h-6" />}
              {searching ? "Matching..." : "Find Matching Jobs"}
            </button>
          </div>

          {status && <p className="text-xs uppercase tracking-widest text-slate-500">{status}</p>}
        </div>

        {/* Matches */}
        {matches && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-orange-400" />
              Your Matches
              <span className="text-sm font-normal text-slate-500">
                ({matches.length} of {totalOpen} open)
              </span>
            </h2>

            {matches.length === 0 ? (
              <div className="glass rounded-3xl p-12 text-center text-slate-500">
                No open vacancies to match against yet. Check back once recruiters have posted some.
              </div>
            ) : (
              matches.map((job) => {
                const pct = Math.round(job.match_score * 100);
                const strong = pct >= 60;
                const weak = pct < 35;
                return (
                  <div key={job.id} className="glass rounded-3xl p-6 space-y-4">
                    <div className="flex items-start justify-between gap-5 flex-wrap">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="text-lg font-semibold">{job.title}</h3>
                          {job.already_applied && (
                            <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold uppercase tracking-wider flex items-center gap-1">
                              <CheckCircle2 className="w-3 h-3" /> Applied
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-slate-400 mt-0.5">{job.company}</div>
                        <div className="flex items-center gap-3 text-xs text-slate-500 mt-2 flex-wrap">
                          {job.location && (
                            <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{job.location}</span>
                          )}
                          <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{job.employment_type}</span>
                          {job.experience_level && <span>{job.experience_level}</span>}
                          {job.salary_range && <span className="text-slate-400">{job.salary_range}</span>}
                        </div>
                      </div>

                      <div className="text-right shrink-0">
                        <div
                          className={`text-4xl font-black ${
                            strong ? "text-emerald-400" : weak ? "text-slate-500" : "text-orange-400"
                          }`}
                        >
                          {pct}%
                        </div>
                        <div className="text-[10px] uppercase tracking-wider text-slate-600">match</div>
                      </div>
                    </div>

                    <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${pct}%` }}
                        className={`h-full ${strong ? "bg-emerald-500" : weak ? "bg-slate-600" : "bg-gradient-to-r from-orange-500 to-red-500"}`}
                      />
                    </div>

                    {job.skills.length > 0 && (
                      <div className="flex flex-wrap gap-1.5">
                        {job.skills.map((s) => (
                          <span key={s} className="px-2 py-0.5 rounded-md bg-white/5 text-[11px] text-slate-400">{s}</span>
                        ))}
                      </div>
                    )}

                    <button
                      onClick={() => setOpenId(openId === job.id ? null : job.id)}
                      className="text-sm text-orange-400 hover:underline"
                    >
                      {openId === job.id ? "Hide details" : "View details & apply"}
                    </button>

                    <AnimatePresence>
                      {openId === job.id && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          className="space-y-4 overflow-hidden"
                        >
                          {job.description && (
                            <Section title="About the role">{job.description}</Section>
                          )}
                          {job.requirements && (
                            <Section title="Requirements">{job.requirements}</Section>
                          )}

                          <div className="rounded-2xl bg-black/20 border border-white/5 p-4 text-xs text-slate-500 flex gap-6">
                            <span>Relevance <strong className="text-slate-300">{(job.relevance * 100).toFixed(1)}%</strong></span>
                            <span>Model fit <strong className="text-slate-300">{(job.fit * 100).toFixed(1)}%</strong></span>
                          </div>

                          {deep[job.id] && (
                            <div className="rounded-2xl border border-orange-500/10 bg-orange-500/5 p-4 space-y-2">
                              <h4 className="text-sm font-bold text-orange-400 flex items-center gap-2">
                                <Lightbulb className="w-4 h-4" />
                                AI verdict: {deep[job.id].decision} ({deep[job.id].probability}%)
                              </h4>
                              <p className="text-sm text-slate-300 italic leading-relaxed">
                                &ldquo;{deep[job.id].advice}&rdquo;
                              </p>
                            </div>
                          )}

                          {!job.already_applied && (
                            <textarea
                              value={coverNote}
                              onChange={(e) => setCoverNote(e.target.value)}
                              placeholder="Optional note to the recruiter..."
                              className="w-full bg-black/30 border border-white/5 rounded-2xl p-4 h-24 focus:ring-2 focus:ring-orange-500/50 outline-none resize-none text-sm"
                            />
                          )}

                          <div className="flex gap-3 flex-wrap">
                            <button
                              onClick={() => runDeepDive(job.id)}
                              disabled={analyzing === job.id}
                              className="px-5 py-2.5 glass hover:bg-white/5 disabled:opacity-40 rounded-xl font-semibold flex items-center gap-2 text-sm"
                            >
                              {analyzing === job.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4 text-orange-400" />}
                              {analyzing === job.id ? "Analyzing..." : "Get AI feedback"}
                            </button>

                            <button
                              onClick={() => handleApply(job.id)}
                              disabled={job.already_applied || applying === job.id}
                              className="px-6 py-2.5 bg-orange-600 hover:bg-orange-500 disabled:bg-stone-800 disabled:text-stone-500 rounded-xl font-semibold flex items-center gap-2 text-sm"
                            >
                              {applying === job.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                              {job.already_applied ? "Already applied" : "Apply"}
                            </button>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                );
              })
            )}
          </div>
        )}
      </main>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5">{title}</h4>
      <p className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">{children}</p>
    </div>
  );
}
