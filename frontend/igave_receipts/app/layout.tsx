import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "../globals.css";


const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
});


export const metadata: Metadata = {
  title: "iSave App",
  description: "Intelligent Receipt Tracker",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    /* 🚨 CRITICAL FIX: 
       I removed className="dark" from the <html> tag below.
       It should just be <html lang="en" ...>
    */
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} antialiased`}>

        {children}
      </body>
    </html>
  );
}