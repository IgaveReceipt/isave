"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/dashboard", label: "Dashboard", icon: "🏠" },
  { href: "/today", label: "Today", icon: "📅" },
  { href: "/day", label: "Day", icon: "📅" },
  { href: "/month", label: "Month", icon: "📆" },
  { href: "/year", label: "Year", icon: "🗓️" },
  { href: "/period", label: "Period", icon: "⏳" },
];

export default function DashboardNav() {
  const pathname = usePathname();

  return (
    <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mb-8">
      {links.map((l) => {
        const active = pathname === l.href;
        return (
          <Link
            key={l.href}
            href={l.href}
            className={`border p-3 rounded-xl text-center transition
              ${active ? "bg-white/25 border-white/30" : "bg-white/5 border-white/10 hover:bg-white/20"}
            `}
          >
            <span className="block text-xl">{l.icon}</span>
            <span className="text-sm font-bold text-white">{l.label}</span>
          </Link>
        );
      })}
    </div>
  );
}
