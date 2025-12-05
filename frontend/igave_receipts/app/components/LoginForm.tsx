"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginForm() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const res = await fetch("http://127.0.0.1:8000/api/login/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await res.json();

    if (res.ok) {
      localStorage.setItem("username", data.username);
        localStorage.setItem("is_staff", data.is_staff);

  router.push(`/dashboard?user=${username}`);

    } else {
      setMessage(data.error || "Login failed");
    }
  };

  return (
    <div className="backdrop-blur-xl bg-white/10 border border-white/20 shadow-2xl rounded-2xl p-10 w-full max-w-md">
      <h2 className="text-3xl font-semibold text-white text-center mb-6">
        Login
      </h2>

      <form onSubmit={handleLogin} className="space-y-5">
        <div>
          <label className="text-white/80">Username</label>
          <input
            type="text"
            className="w-full mt-1 px-4 py-2 rounded-xl bg-white/20 text-white placeholder-white/60
            border border-white/30 focus:outline-none focus:ring-2 focus:ring-indigo-300"
            placeholder="Enter username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="text-white/80">Password</label>
          <input
            type="password"
            className="w-full mt-1 px-4 py-2 rounded-xl bg-white/20 text-white placeholder-white/60
            border border-white/30 focus:outline-none focus:ring-2 focus:ring-pink-300"
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button
          type="submit"
          className="w-full py-3 rounded-xl bg-white/30 text-white font-medium
          hover:bg-white/40 transition backdrop-blur-md border border-white/20 shadow-lg"
        >
          Login
        </button>
      </form>

      {message && (
        <p
          className={`mt-4 text-center font-medium ${
            message.includes("successful") ? "text-green-300" : "text-red-300"
          }`}
        >
          {message}
        </p>
      )}

      <p className="text-center text-white/70 mt-6">
        Don’t have an account?{" "}
        <a href="/register" className="text-white underline hover:text-pink-200">
          Register
        </a>
      </p>
    </div>
  );
}