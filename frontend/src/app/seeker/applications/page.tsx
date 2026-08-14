"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { History, Loader2, AlertCircle, MapPin, Building2 } from "lucide-react";
import AppHeader from "@/components/AppHeader";
import { useAuthGuard } from "@/lib/useAuth";
import { myApplications, type Application, type ApplicationStatus } from "@/lib/api";

const STATUS_STYLES: Record<ApplicationStatus, string> = {
  submitted: "bg-slate-500/10 text-slate-300 border-slate-500/20",
  reviewed: "bg-sky-500/10 text-sky-400 border-sky-500/20",
  shortlisted: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  rejected: "bg-red-500/10 text-red-400 border-red-500/20",
};

const STATUS_HELP: Record<ApplicationStatus, string> = {
  submitted: "Sent — the recruiter hasn't opened it yet.",
  reviewed: "The recruiter has read your application.",
  shortlisted: "You're on the shortlist.",
  rejected: "Not moving forward this time.",
};

export default function ApplicationsPage() {
  const { user, loading: booting } = useAuthGuard("seeker");
  const [applications, setApplications] = useState<Application[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    myApplications()
      .then(setApplications)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load applications."))
      .finally(() => setLoading(false));
  }, [user]);

  if (booting) {
    return (
      <div className="min-h-screen flex items-center justify-center text-slate-400 gap-3">
        <Loader2 className="w-6 h-6 animate-spin text-orange-400" />
        Loading...
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <AppHeader user={user} />

      <main className="flex-1 p-8 max-w-4xl mx-auto w-full space-y-6">
        {error && (
          <div className="flex items-start gap-2 rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <History className="w-6 h-6 text-orange-400" />
            My Applications
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Every vacancy you&apos;ve applied to, and where it stands.
          </p>
        </div>

        {loading ? (
          <div className="flex items-center gap-2 text-slate-500 py-12 justify-center">
            <Loader2 className="w-5 h-5 animate-spin" /> Loading...
          </div>
        ) : applications.length === 0 ? (
          <div className="glass rounded-3xl p-12 text-center text-slate-500 space-y-3">
            <p>You haven&apos;t applied to anything yet.</p>
            <Link href="/seeker" className="text-orange-400 hover:underline text-sm">
              Find matching jobs →
            </Link>
          </div>
        ) : (
          <ul className="space-y-3">
            {applications.map((app) => (
              <li key={app.id} className="glass rounded-3xl p-6 space-y-3">
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div className="min-w-0">
                    <h3 className="text-lg font-semibold">{app.job?.title}</h3>
                    <div className="flex items-center gap-3 text-xs text-slate-500 mt-1 flex-wrap">
                      {app.job?.company && (
                        <span className="flex items-center gap-1"><Building2 className="w-3 h-3" />{app.job.company}</span>
                      )}
                      {app.job?.location && (
                        <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{app.job.location}</span>
                      )}
                      {app.created_at && <span>Applied {new Date(app.created_at).toLocaleDateString()}</span>}
                    </div>
                  </div>
                  <div className="flex items-center gap-4 shrink-0">
                    <div className="text-right">
                      <div className="text-xl font-black text-orange-400">
                        {(app.match_score * 100).toFixed(0)}%
                      </div>
                      <div className="text-[10px] uppercase tracking-wider text-slate-600">match</div>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider border ${STATUS_STYLES[app.status]}`}
                    >
                      {app.status}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-500">{STATUS_HELP[app.status]}</p>

                {app.cover_note && (
                  <p className="text-sm text-slate-400 italic border-l-2 border-orange-500/30 pl-3">
                    &ldquo;{app.cover_note}&rdquo;
                  </p>
                )}

                {app.job?.status === "closed" && (
                  <p className="text-xs text-slate-600">This vacancy has since been closed.</p>
                )}
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}
