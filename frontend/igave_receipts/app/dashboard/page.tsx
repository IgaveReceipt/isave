"use client";

import { useEffect, useState, useRef } from "react";
import DashboardLayout from "../components/DashboardLayout";
import VerifyReceiptForm from "../components/VerifyReceiptForm";
import { scanReceipt } from "../services/api";
import { ReceiptData } from "../types";

export default function DashboardPage() {
  const [username, setUsername] = useState("");
  
  // --- NEW STATE ---
  const [draftReceipt, setDraftReceipt] = useState<ReceiptData | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanError, setScanError] = useState("");
  
  // This reference allows us to click the hidden file input via code
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const user = localStorage.getItem("username");
    if (user) {
      setUsername(user);
    }
  }, []);

  // 1. Handle File Selection
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsScanning(true);
    setScanError("");

    try {
      // Call the API we updated earlier
      const data = await scanReceipt(file);
      setDraftReceipt(data); // Switch to "Verify Mode"
    } catch (err) {
      setScanError("Failed to scan receipt. Please try again.");
    } finally {
      setIsScanning(false);
      // Reset the input so we can scan the same file again if needed
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  // 2. Render "Verify Mode" if we have data
  if (draftReceipt) {
    return (
      <DashboardLayout>
        <VerifyReceiptForm 
          initialData={draftReceipt}
          onCancel={() => setDraftReceipt(null)} // Go back to menu
          onSuccess={() => {
            setDraftReceipt(null); // Go back to menu
            alert("Receipt saved successfully!");
          }}
        />
      </DashboardLayout>
    );
  }

  // 3. Render "Menu Mode" (Default)
  return (
    <DashboardLayout>
      <h1 className="text-4xl font-bold mb-4">
        Welcome, {username} 👋
      </h1>

      <p className="opacity-80 mb-6">
        {isScanning ? "Scanning receipt... " : "What would you like to do today?"}
      </p>

      {scanError && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {scanError}
        </div>
      )}

      <div className="flex flex-col gap-4 mt-4 max-w-md">
        
        {/* --- THE SCAN BUTTON --- */}
        {/* Hidden Input */}
        <input 
          type="file" 
          hidden 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          accept="image/*"
        />
        
        <button
          onClick={() => fileInputRef.current?.click()} // Trigger hidden input
          disabled={isScanning}
          className="bg-blue-600 text-white px-6 py-4 rounded-xl hover:bg-blue-700 transition flex items-center justify-center gap-2 font-bold shadow-lg"
        >
          {isScanning ? (
            <span>Processing...</span>
          ) : (
            <>
              <span>📸</span> Scan New Receipt
            </>
          )}
        </button>

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