
"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "../components/DashboardLayout";

export default function DashboardPage() {
  const [username, setUsername] = useState("");

  useEffect(() => {
    const user = localStorage.getItem("username");
    if (user) {
      setUsername(user);
    }
  }, []);

  return (
    <DashboardLayout>
      <h1 className="text-4xl font-bold mb-4">
        Welcome, {username} 👋
      </h1>

      <p className="opacity-80 mb-6">
        This is your dashboard. Security will be added later.
      </p>

      <div className="flex flex-col gap-4 mt-4">
        <button
          onClick={() => (window.location.href = "/users")}
          className="bg-purple-300/60 dark:bg-purple-700/60 px-6 py-3 rounded-xl hover:opacity-80 transition"
        >
          View Users
        </button>

        <button
          onClick={() => {
            localStorage.clear();
            window.location.href = "/login";
          }}
          className="bg-red-400/70 px-6 py-3 rounded-xl hover:opacity-80 transition"
        >
          Logout
        </button>
      </div>
    </DashboardLayout>
  );
}
