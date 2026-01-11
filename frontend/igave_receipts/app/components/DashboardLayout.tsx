"use client";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      
      {/* The Glassy Card Container */}
      <main className="w-full max-w-lg bg-white/10 backdrop-blur-lg border border-white/20 rounded-3xl p-8 shadow-2xl">
        {children}
      </main>

      {/* Footer / Copyright */}
      <footer className="mt-8 text-white/40 text-sm">
        © {new Date().getFullYear()} iSave App
      </footer>
    </div>
  );
}
