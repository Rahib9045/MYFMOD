"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { User, Mail, Lock, Loader2, BrainCircuit, AlertCircle, Building2, Briefcase, FileUser } from "lucide-react";
import { register, homeFor, type Role } from "@/lib/api";

export default function RegisterPage() {
  const [role, setRole] = useState<Role>("seeker");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [company, setCompany] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setLoading(true);
    try {
      const user = await register({ name, email, password, role, company });
      router.push(homeFor(user));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed.");
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass max-w-md w-full p-8 rounded-3xl shadow-2xl"
      >
        <div className="flex flex-col items-center mb-8">
          <div className="p-3 bg-red-500 bg-opacity-20 rounded-2xl mb-4">
            <BrainCircuit className="w-10 h-10 text-red-400" />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-400 to-red-400 bg-clip-text text-transparent">Create Account</h1>
          <p className="text-slate-400 mt-2">Join the future of intelligence recruitment</p>
        </div>

        {/* Role picker — this is fixed once the account exists */}
        <div className="grid grid-cols-2 gap-3 mb-6">
          <button
            type="button"
            onClick={() => setRole("seeker")}
            className={`rounded-2xl border p-4 text-left transition-all ${
              role === "seeker"
                ? "border-orange-500/50 bg-orange-500/10"
                : "border-white/10 bg-black/20 hover:border-white/20"
            }`}
          >
            <FileUser className={`w-5 h-5 mb-2 ${role === "seeker" ? "text-orange-400" : "text-slate-500"}`} />
            <div className="font-semibold text-sm">Job Seeker</div>
            <div className="text-[11px] text-slate-500 mt-1 leading-snug">Upload a CV, get matched, apply</div>
          </button>
          <button
            type="button"
            onClick={() => setRole("recruiter")}
            className={`rounded-2xl border p-4 text-left transition-all ${
              role === "recruiter"
                ? "border-orange-500/50 bg-orange-500/10"
                : "border-white/10 bg-black/20 hover:border-white/20"
            }`}
          >
            <Briefcase className={`w-5 h-5 mb-2 ${role === "recruiter" ? "text-orange-400" : "text-slate-500"}`} />
            <div className="font-semibold text-sm">Recruiter</div>
            <div className="text-[11px] text-slate-500 mt-1 leading-snug">Post vacancies, review applicants</div>
          </button>
        </div>

        {error && (
          <div className="mb-4 flex items-start gap-2 rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-300">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Full Name</label>
            <div className="relative">
              <User className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
              <input
                required
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="John Doe"
                className="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 focus:ring-2 focus:ring-orange-500 focus:outline-none transition-all"
              />
            </div>
          </div>

          {role === "recruiter" && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Company</label>
              <div className="relative">
                <Building2 className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="Northwind Data"
                  className="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 focus:ring-2 focus:ring-orange-500 focus:outline-none transition-all"
                />
              </div>
              <p className="text-[11px] text-slate-500 ml-1">Used as the default on vacancies you post.</p>
            </div>
          )}

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
              <input
                required
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="john@example.com"
                className="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 focus:ring-2 focus:ring-orange-500 focus:outline-none transition-all"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
              <input
                required
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 8 characters"
                className="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 focus:ring-2 focus:ring-orange-500 focus:outline-none transition-all"
              />
            </div>
          </div>

          <button
            disabled={loading}
            className="w-full bg-gradient-to-r from-orange-600 to-red-600 hover:opacity-90 disabled:opacity-50 text-white font-semibold py-3 rounded-xl transition-all flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : `Create ${role === "recruiter" ? "Recruiter" : "Job Seeker"} Account`}
          </button>
        </form>

        <p className="text-center text-slate-500 mt-6 text-sm">
          Already have an account? <Link href="/login" className="text-orange-400 hover:underline">Sign In</Link>
        </p>
      </motion.div>
    </div>
  );
}
