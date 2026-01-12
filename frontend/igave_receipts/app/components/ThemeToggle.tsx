"use client";

import { useEffect, useState } from "react";
import { BsSunFill, BsMoonFill } from "react-icons/bs";

export default function ThemeToggle() {
  const [theme, setTheme] = useState("dark");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Check storage or default to dark
    const saved = localStorage.getItem("theme") || "dark";
    setTheme(saved);
    
    // Apply initial state
    const root = document.documentElement;
    if (saved === "dark") {
      root.classList.add("dark");
      root.style.colorScheme = "dark";
    } else {
      root.classList.remove("dark");
      root.style.colorScheme = "light";
    }
  }, []);

  const toggleTheme = () => {
    const root = document.documentElement;
    const newTheme = theme === "light" ? "dark" : "light";
    
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    
    // ⚡️ FORCE UPDATE THE DOM
    if (newTheme === "dark") {
      root.classList.add("dark");
      root.style.colorScheme = "dark";
    } else {
      root.classList.remove("dark");
      root.style.colorScheme = "light";
    }
  };

  // Prevent hydration mismatch (don't render until client loads)
  if (!mounted) return null;

  return (
    <button
      onClick={toggleTheme}
      className="
      fixed top-6 right-6 z-[9999] cursor-pointer
      bg-white/20 dark:bg-black/40 
      text-yellow-600 dark:text-yellow-300 
      hover:scale-110 active:scale-95
      p-3 rounded-full shadow-xl backdrop-blur-md transition-all border border-white/10"
      title={theme === "light" ? "Switch to Dark Mode" : "Switch to Light Mode"}
    >
      {theme === "light" ? <BsMoonFill size={20} /> : <BsSunFill size={20} />}
    </button>
  );
}