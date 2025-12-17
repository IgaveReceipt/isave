"use client";

import ThemeToggle from "./ThemeToggle";

import { ReactNode } from "react";

export default function AuthLayout({ children }: { children: ReactNode }) {

  return (
    <div className="min-h-screen flex items-center justify-center 
      bg-gradient-to-br from-purple-500 via-purple-400 to-pink-500 
      dark:from-gray-900 dark:via-gray-800 dark:to-black 
      transition-all duration-300 relative">

      
      <div className="absolute top-6 right-6 z-50">
        <ThemeToggle />
      </div>

      
      {children}
    </div>
  );
}
