"use client";

import ThemeToggle from "./ThemeToggle";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="
        min-h-screen flex items-center justify-center 
        bg-gradient-to-br from-purple-500 via-purple-400 to-pink-500 
        dark:from-gray-900 dark:via-gray-800 dark:to-black
        transition-all duration-300 relative
      "
    >
      <ThemeToggle />

      {children}
    </div>
  );
}
