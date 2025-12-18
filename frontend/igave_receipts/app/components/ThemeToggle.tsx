"use client";

import { useEffect, useState } from "react";
import { BsSunFill, BsMoonFill } from "react-icons/bs";

export default function ThemeToggle() {
  const [theme, setTheme] = useState("light");

  useEffect(() => {
    const saved = localStorage.getItem("theme") || "light";
    setTheme(saved);
    document.documentElement.classList.toggle("dark", saved === "dark");
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    document.documentElement.classList.toggle("dark", newTheme === "dark");
  };

  return (
    <button
      onClick={toggleTheme}
      className="
      bg-white/40 dark:bg-gray-700 text-yellow-400 dark:text-yellow-300 
      p-3 rounded-full shadow-lg backdrop-blur-md transition-all"
    >
      {theme === "light" ? <BsMoonFill size={20} /> : <BsSunFill size={20} />}
    </button>

  );
}
