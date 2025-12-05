"use client";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-start p-10 relative">
      {/* Головний контейнер */}
      <div className="w-full max-w-3xl bg-white/10 dark:bg-black/20 backdrop-blur-xl p-10 rounded-2xl shadow-2xl text-center border border-white/10">
        {children}
      </div>
    </div>
  );
}
