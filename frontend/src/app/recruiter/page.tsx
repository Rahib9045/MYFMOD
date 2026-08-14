"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Briefcase,
  Plus,
  Users,
  Trash2,
  Loader2,
  AlertCircle,
  MapPin,
  Clock,
  X,
  ChevronRight,
  Mail,
  FileText,
} from "lucide-react";
import AppHeader from "@/components/AppHeader";
import { useAuthGuard } from "@/lib/useAuth";
import {
  createJob,
  myJobs,
  updateJob,
  deleteJob,
  jobApplications,
  setApplicationStatus,
  type Job,
  type Application,
  type ApplicationStatus,
} from "@/lib/api";

const EMPTY = {
  title: "",
  location: "",
  employment_type: "Full-time",
  experience_level: "Mid",
  salary_range: "",
  description: "",
  requirements: "",
  skills: "",
};

const STATUS_STYLES: Record<ApplicationStatus, string> = {
  submitted: "bg-slate-500/10 text-slate-300 border-slate-500/20",
  reviewed: "bg-sky-500/10 text-sky-400 border-sky-500/20",
  shortlisted: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  rejected: "bg-red-500/10 text-red-400 border-red-500/20",
};

export default function RecruiterPage() {
  const { user, loading: booting } = useAuthGuard("recruiter");

  const [jobs, setJobs] = useState<Job[]>([]);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);

  const [openJob, setOpenJob] = useState<Job | null>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [loadingApps, setLoadingApps] = useState(false);
  const [expanded, setExpanded] = useState<number | null>(null);

  const refresh = useCallback(async () => {
    try {
      setJobs(await myJobs());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load vacancies.");
    }
  }, []);

  useEffect(() => {
    if (user) refresh();
  }, [user, refresh]);

  const set = (key: keyof typeof EMPTY) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      await createJob({
        ...form,
        skills: form.skills.split(",").map((s) => s.trim()).filter(Boolean),
      });
      setForm(EMPTY);
      setShowForm(false);
      refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not post the vacancy.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteJob(id);
      setJobs((prev) => prev.filter((j) => j.id !== id));
      if (openJob?.id === id) setOpenJob(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete the vacancy.");
    }
  };

  const toggleStatus = async (job: Job) => {
    try {
      const updated = await updateJob(job.id, { status: job.status === "open" ? "closed" : "open" });
      setJobs((prev) => prev.map((j) => (j.id === job.id ? updated : j)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update the vacancy.");
    }
  };

  const viewApplicants = async (job: Job) => {
    setOpenJob(job);
    setLoadingApps(true);
    setExpanded(null);
    try {
      const data = await jobApplications(job.id);
      setApplications(data.applications);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load applicants.");
    } finally {
      setLoadingApps(false);
    }
  };

  const moveApplicant = async (id: number, status: ApplicationStatus) => {
    try {
      const updated = await setApplicationStatus(id, status);
      setApplications((prev) => prev.map((a) => (a.id === id ? { ...a, status: updated.status } : a)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update the applicant.");
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

      <main className="flex-1 p-8 max-w-7xl mx-auto w-full space-y-6">
        {error && (
          <div className="flex items-start gap-2 rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Briefcase className="w-6 h-6 text-orange-400" />
              Your Vacancies
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Posted vacancies are matched against every job seeker&apos;s CV automatically.
            </p>
          </div>
          <button
            onClick={() => setShowForm((s) => !s)}
            className="bg-orange-600 hover:bg-orange-500 px-5 py-3 rounded-2xl font-semibold flex items-center gap-2 transition-all"
          >
            {showForm ? <X className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
            {showForm ? "Cancel" : "Post a Vacancy"}
          </button>
        </div>

        <AnimatePresence>
          {showForm && (
            <motion.form
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              onSubmit={handleCreate}
              className="glass rounded-3xl p-8 space-y-5 overflow-hidden"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Field label="Job Title *">
                  <input required value={form.title} onChange={set("title")} placeholder="Senior Data Analyst" className={inputCls} />
                </Field>
                <Field label="Location">
                  <input value={form.location} onChange={set("location")} placeholder="London / Remote" className={inputCls} />
                </Field>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Field label="Employment Type">
                  <select value={form.employment_type} onChange={set("employment_type")} className={inputCls}>
                    {["Full-time", "Part-time", "Contract", "Internship"].map((t) => (
                      <option key={t} value={t} className="bg-stone-900">{t}</option>
                    ))}
                  </select>
                </Field>
                <Field label="Experience Level">
                  <select value={form.experience_level} onChange={set("experience_level")} className={inputCls}>
                    {["Entry", "Junior", "Mid", "Senior", "Lead"].map((t) => (
                      <option key={t} value={t} className="bg-stone-900">{t}</option>
                    ))}
                  </select>
                </Field>
                <Field label="Salary Range">
                  <input value={form.salary_range} onChange={set("salary_range")} placeholder="£55k – £70k" className={inputCls} />
                </Field>
              </div>

              <Field label="Description">
                <textarea value={form.description} onChange={set("description")} placeholder="What the role involves day to day..." className={`${inputCls} h-28 resize-none`} />
              </Field>

              <Field label="Requirements">
                <textarea value={form.requirements} onChange={set("requirements")} placeholder="5+ years SQL, Python, Tableau. BSc Statistics or equivalent..." className={`${inputCls} h-28 resize-none`} />
              </Field>

              <Field label="Key Skills (comma separated)">
                <input value={form.skills} onChange={set("skills")} placeholder="SQL, Python, Tableau, dashboards" className={inputCls} />
              </Field>

              <p className="text-xs text-slate-500">
                Description, requirements and skills all feed the matching model — the more specific they are, the
                better the ranking.
              </p>

              <button
                disabled={saving || !form.title.trim()}
                className="bg-orange-600 hover:bg-orange-500 disabled:opacity-40 px-6 py-3 rounded-2xl font-semibold flex items-center gap-2"
              >
                {saving ? <Loader2 className="w-5 h-5 animate-spin" /> : <Plus className="w-5 h-5" />}
                Publish Vacancy
              </button>
            </motion.form>
          )}
        </AnimatePresence>

        {jobs.length === 0 ? (
          <div className="glass rounded-3xl p-12 text-center text-slate-500">
            No vacancies yet. Post one and job seekers will start matching against it.
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {jobs.map((job) => (
              <div key={job.id} className="glass rounded-3xl p-6 space-y-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h3 className="text-lg font-semibold truncate">{job.title}</h3>
                    <div className="flex items-center gap-3 text-xs text-slate-500 mt-1.5 flex-wrap">
                      {job.location && (
                        <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{job.location}</span>
                      )}
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{job.employment_type}</span>
                      {job.salary_range && <span>{job.salary_range}</span>}
                    </div>
                  </div>
                  <span
                    className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider shrink-0 ${
                      job.status === "open"
                        ? "bg-emerald-500/10 text-emerald-400"
                        : "bg-slate-500/10 text-slate-400"
                    }`}
                  >
                    {job.status}
                  </span>
                </div>

                {job.skills.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {job.skills.slice(0, 6).map((s) => (
                      <span key={s} className="px-2 py-0.5 rounded-md bg-white/5 text-[11px] text-slate-400">{s}</span>
                    ))}
                  </div>
                )}

                <div className="flex items-center gap-2 pt-1 flex-wrap">
                  <button
                    onClick={() => viewApplicants(job)}
                    className="flex-1 min-w-[140px] glass-hover border border-white/5 rounded-xl px-4 py-2.5 text-sm font-medium flex items-center justify-center gap-2"
                  >
                    <Users className="w-4 h-4 text-orange-400" />
                    {job.applicant_count ?? 0} applicant{job.applicant_count === 1 ? "" : "s"}
                    <ChevronRight className="w-4 h-4 text-slate-600" />
                  </button>
                  <button
                    onClick={() => toggleStatus(job)}
                    className="glass-hover border border-white/5 rounded-xl px-4 py-2.5 text-sm text-slate-300"
                  >
                    {job.status === "open" ? "Close" : "Reopen"}
                  </button>
                  <button
                    onClick={() => handleDelete(job.id)}
                    className="p-2.5 text-slate-600 hover:text-red-400 transition-colors"
                    aria-label={`Delete ${job.title}`}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Applicants panel */}
        <AnimatePresence>
          {openJob && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="glass rounded-3xl p-8 space-y-5"
            >
              <div className="flex items-center justify-between gap-4">
                <div>
                  <h2 className="text-xl font-semibold flex items-center gap-2">
                    <Users className="w-5 h-5 text-orange-400" />
                    Applicants — {openJob.title}
                  </h2>
                  <p className="text-xs text-slate-500 mt-1">Ranked by how well each CV matches this vacancy.</p>
                </div>
                <button onClick={() => setOpenJob(null)} className="text-slate-500 hover:text-white">
                  <X className="w-5 h-5" />
                </button>
              </div>

              {loadingApps ? (
                <div className="flex items-center gap-2 text-slate-500 py-8 justify-center">
                  <Loader2 className="w-5 h-5 animate-spin" /> Loading applicants...
                </div>
              ) : applications.length === 0 ? (
                <p className="text-center text-slate-500 py-8">No applications yet.</p>
              ) : (
                <ul className="space-y-3">
                  {applications.map((app) => (
                    <li key={app.id} className="rounded-2xl border border-white/5 bg-black/20 p-5 space-y-3">
                      <div className="flex items-start justify-between gap-4 flex-wrap">
                        <div className="min-w-0">
                          <div className="font-semibold text-slate-100">{app.applicant?.name}</div>
                          <div className="text-xs text-slate-500 flex items-center gap-1 mt-0.5">
                            <Mail className="w-3 h-3" />
                            {app.applicant?.email}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-black text-orange-400">
                            {(app.match_score * 100).toFixed(1)}%
                          </div>
                          <div className="text-[10px] uppercase tracking-wider text-slate-600">CV match</div>
                        </div>
                      </div>

                      {app.cover_note && (
                        <p className="text-sm text-slate-400 italic border-l-2 border-orange-500/30 pl-3">
                          &ldquo;{app.cover_note}&rdquo;
                        </p>
                      )}

                      <div className="flex items-center gap-2 flex-wrap">
                        {(["submitted", "reviewed", "shortlisted", "rejected"] as ApplicationStatus[]).map((s) => (
                          <button
                            key={s}
                            onClick={() => moveApplicant(app.id, s)}
                            className={`px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider border transition-all ${
                              app.status === s ? STATUS_STYLES[s] : "border-white/5 text-slate-600 hover:text-slate-300"
                            }`}
                          >
                            {s}
                          </button>
                        ))}
                        <button
                          onClick={() => setExpanded(expanded === app.id ? null : app.id)}
                          className="ml-auto text-xs text-slate-400 hover:text-white flex items-center gap-1"
                        >
                          <FileText className="w-3.5 h-3.5" />
                          {expanded === app.id ? "Hide CV" : "View CV"}
                        </button>
                      </div>

                      {expanded === app.id && (
                        <pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap rounded-xl bg-black/40 p-4 text-xs text-slate-400 leading-relaxed">
                          {app.cv_text}
                        </pre>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

const inputCls =
  "w-full bg-black/30 border border-white/5 rounded-xl px-4 py-2.5 focus:ring-2 focus:ring-orange-500/50 outline-none transition-all";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-bold text-slate-500 uppercase tracking-widest ml-1">{label}</label>
      {children}
    </div>
  );
}
