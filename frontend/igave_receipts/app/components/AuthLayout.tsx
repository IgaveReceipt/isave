"use client";

import ThemeToggle from "./ThemeToggle";

import { ReactNode } from "react";

export default function AuthLayout({ children }: { children: ReactNode }) {

  return (
    <div className="min-h-screen flex items-center justify-center">


      
      <div className="absolute top-6 right-6 z-50">
        <ThemeToggle />
      </div>

      
      {children}
    </div>
  );
}
