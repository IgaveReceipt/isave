"use client";

import ThemeToggle from "./ThemeToggle"; 

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col p-4 md:p-6 relative bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
      
      {/* 2. ADD THE BUTTON HERE (Absolute position puts it in the top-right corner) */}
      <div className="absolute top-4 right-4 z-10">
        <ThemeToggle />
      </div>

      <main className="w-full max-w-7xl mx-auto flex-1 bg-white/10 backdrop-blur-lg border border-white/20 rounded-3xl p-6 md:p-8 shadow-2xl">
        {children}
      </main>

      <footer className="mt-8 text-center text-white/40 text-sm">
        © {new Date().getFullYear()} iSave App
      </footer>
    </div>
  );
}