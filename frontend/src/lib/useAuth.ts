"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { me, homeFor, type Role, type User } from "@/lib/api";

/**
 * Verifies the session against the server (not just localStorage) and, if a
 * role is required, bounces the wrong role to its own portal rather than
 * showing it a page whose API calls would all 403.
 */
export function useAuthGuard(requiredRole?: Role) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    me()
      .then((u) => {
        if (cancelled) return;
        if (requiredRole && u.role !== requiredRole) {
          router.replace(homeFor(u));
          return;
        }
        setUser(u);
        setLoading(false);
      })
      .catch(() => {
        if (!cancelled) router.replace("/login");
      });
    return () => {
      cancelled = true;
    };
  }, [router, requiredRole]);

  return { user, setUser, loading };
}
