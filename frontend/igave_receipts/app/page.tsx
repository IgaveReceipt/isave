export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center
                    bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
      <h1 className="text-4xl font-bold text-white mb-6">Welcome ✨</h1>
      <p className="text-white/80 mb-6">Please choose an option below</p>

      <div className="flex gap-4">
        <a href="/login" className="px-6 py-2 rounded-lg bg-white/20 text-white hover:bg-white/30">Login</a>
        <a href="/register" className="px-6 py-2 rounded-lg bg-white/20 text-white hover:bg-white/30">Register</a>
      </div>
    </div>
  );
}
