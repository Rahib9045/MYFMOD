"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Lock, Mail, Loader2, BrainCircuit, AlertCircle } from "lucide-react";
import { login } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign in failed.");
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass max-w-md w-full p-8 rounded-3xl shadow-2xl"
      >
        <div className="flex flex-col items-center mb-8">
          <div className="p-3 bg-orange-500 bg-opacity-20 rounded-2xl mb-4">
            <BrainCircuit className="w-10 h-10 text-orange-400" />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-400 to-red-400 bg-clip-text text-transparent">Welcome Back</h1>
          <p className="text-slate-400 mt-2">Sign in to access your recruitment portal</p>
        </div>

        {error && (
          <div className="mb-4 flex items-start gap-2 rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-300">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
              <input
                required
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="email@example.com"
                className="w-full bg-slate-900 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 focus:ring-2 focus:ring-orange-500 focus:outline-none transition-all"
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
                placeholder="••••••••"
                className="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 focus:ring-2 focus:ring-orange-500 focus:outline-none transition-all"
              />
            </div>
          </div>

          <button
            disabled={loading}
            className="w-full bg-gradient-to-r from-orange-600 to-red-600 hover:opacity-90 disabled:opacity-50 text-white font-semibold py-3 rounded-xl transition-all flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Sign In"}
          </button>
        </form>

        <p className="text-center text-slate-500 mt-6 text-sm">
          Don&apos;t have an account? <Link href="/register" className="text-orange-400 hover:underline">Register now</Link>
        </p>
      </motion.div>
    </div>
  );
}
