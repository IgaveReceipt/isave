import ThemeToggle from "./components/ThemeToggle"; // <--- Import it

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative">
      {/* The Toggle Button (Floats in top right) */}
      <ThemeToggle />

      <h1 className="text-5xl font-extrabold text-white mb-6 drop-shadow-lg">
        Welcome to iSave ✨
      </h1>
      <p className="text-white/80 mb-8 text-lg font-light">
        The Intelligent Receipt Tracker
      </p>

      <div className="flex gap-4">
        <a 
          href="/login" 
          className="px-8 py-3 rounded-xl bg-white/20 text-white font-bold backdrop-blur-md border border-white/20 hover:bg-white/30 transition shadow-lg"
        >
          Login
        </a>
        <a 
          href="/register" 
          className="px-8 py-3 rounded-xl bg-purple-600/80 text-white font-bold backdrop-blur-md border border-purple-400/30 hover:bg-purple-600 transition shadow-lg"
        >
          Register
        </a>
      </div>
    </div>
  );
}