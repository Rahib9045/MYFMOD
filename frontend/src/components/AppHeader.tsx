"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { BrainCircuit, LogOut } from "lucide-react";
import { logout, type User } from "@/lib/api";

/** Nav differs per role — a seeker has no vacancies, a recruiter has no CV. */
const NAV: Record<string, { href: string; label: string }[]> = {
  recruiter: [
    { href: "/recruiter", label: "Vacancies" },
    { href: "/dashboard", label: "Manual Screening" },
  ],
  seeker: [
    { href: "/seeker", label: "Find Jobs" },
    { href: "/seeker/analyze", label: "CV Analysis" },
    { href: "/seeker/applications", label: "My Applications" },
  ],
};

export default function AppHeader({ user }: { user: User | null }) {
  const router = useRouter();
  const pathname = usePathname();
  const links = user ? NAV[user.role] ?? [] : [];

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <header className="glass border-b border-white/5 py-4 px-8 flex justify-between items-center sticky top-0 z-50 gap-6">
      <div className="flex items-center gap-8 min-w-0">
        <div className="flex items-center gap-3 shrink-0">
          <div className="p-2 bg-orange-500/20 rounded-xl">
            <BrainCircuit className="w-6 h-6 text-orange-400" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white/90 hidden sm:block">
            AI Recruitment <span className="text-orange-400">Intelligence</span>
          </span>
        </div>

        <nav className="flex items-center gap-1">
          {links.map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  active ? "bg-orange-500/15 text-orange-400" : "text-slate-400 hover:text-white"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="flex items-center gap-5 shrink-0">
        <div className="text-right hidden sm:block">
          <div className="text-sm text-slate-200 font-medium leading-tight">{user?.name}</div>
          <div className="text-[11px] text-slate-500 uppercase tracking-wider">
            {user?.role === "recruiter" ? user.company || "Recruiter" : "Job Seeker"}
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span className="text-sm font-medium hidden md:block">Logout</span>
        </button>
      </div>
    </header>
  );
}
