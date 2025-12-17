import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "../globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Auth UI",
  description: "Login/Register demo",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
  className="
    min-h-screen 
    bg-gradient-to-br from-purple-500 via-pink-500 to-fuchsia-600
    dark:bg-gradient-to-br dark:from-gray-900 dark:via-gray-800 dark:to-black
    text-gray-900 dark:text-gray-100
    transition-all duration-500
  "
>
        {children}
      </body>
    </html>
  );
}
