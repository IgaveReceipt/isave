"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function RegisterForm() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const res = await fetch("http://127.0.0.1:8000/api/register/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await res.json();

    if (res.ok) {
      setMessage("User created successfully!");
      setTimeout(() => router.push("/login"), 1200); // redirect to login
    } else {
      setMessage(data.error || "Registration failed");
    }
  };

  return (
    <div className="backdrop-blur-xl bg-white/10 dark:bg-black/20 border border-white/20 dark:border-white/10 
                    shadow-2xl rounded-2xl p-10 w-full max-w-md">

      <h2 className="text-3xl font-semibold text-white text-center mb-6 drop-shadow-md">
        Create Account
      </h2>

      <form onSubmit={handleRegister} className="space-y-5">
        {/* Username */}
        <div>
          <label className="text-white/80">Username</label>
          <input
            type="text"
            className="w-full mt-1 px-4 py-2 rounded-xl bg-white/20 text-white placeholder-white/60
                       border border-white/30 focus:outline-none focus:ring-2 focus:ring-pink-300"
            placeholder="Enter username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        {/* Password */}
        <div>
          <label className="text-white/80">Password</label>
          <input
            type="password"
            className="w-full mt-1 px-4 py-2 rounded-xl bg-white/20 text-white placeholder-white/60
                       border border-white/30 focus:outline-none focus:ring-2 focus:ring-indigo-300"
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        {/* Submit */}
        <button
          type="submit"
          className="w-full py-3 rounded-xl bg-white/30 text-white font-medium
                     hover:bg-white/40 transition backdrop-blur-md border border-white/20 shadow-lg"
        >
          Register
        </button>
      </form>

      {/* Message */}
      {message && (
        <p
          className={`mt-4 text-center font-medium ${
            message.includes("successfully") ? "text-green-300" : "text-red-300"
          }`}
        >
          {message}
        </p>
      )}

      {/* Link to login */}
      <p className="text-center text-white/70 mt-6">
        Already have an account?{" "}
        <a href="/login" className="text-white underline hover:text-pink-200">
          Login
        </a>
      </p>
    </div>
  );
}