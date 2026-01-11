"use client";

import { useEffect, useState, useRef } from "react";
import DashboardLayout from "../components/DashboardLayout";
import VerifyReceiptForm from "../components/VerifyReceiptForm";
import RecordsList, { ReceiptItem } from "../components/RecordsList";
import { scanReceipt, exportCSV, deleteReceipt, apiGet } from "../services/api"; // <--- Import deleteReceipt
import { ReceiptData } from "../types";

export default function DashboardPage() {
  // ... (keep existing state) ...
  const [username, setUsername] = useState("");
  const [history, setHistory] = useState<ReceiptItem[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [draftReceipt, setDraftReceipt] = useState<ReceiptData | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [scanError, setScanError] = useState("");
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const user = localStorage.getItem("username");
    if (user) setUsername(user);
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const data = await apiGet<ReceiptItem[]>("/api/receipts/");
      if (data) setHistory(data);
    } catch (e) {
      console.error("Failed to load history", e);
    }
  };

  // ... (keep handleFileChange) ...
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      setIsScanning(true);
      setScanError("");
      try {
        const data = await scanReceipt(file);
        setDraftReceipt(data);
      } catch (err) {
        setScanError("Failed to scan receipt.");
      } finally {
        setIsScanning(false);
        if (fileInputRef.current) fileInputRef.current.value = "";
      }
    };


  // ... (keep toggleSelection) ...
  const toggleSelection = (id: number) => {
      setSelectedIds(prev => 
        prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
      );
    };

  // --- NEW: Handle Delete ---
  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this receipt?")) return;

    try {
      await deleteReceipt(id);
      // Remove from UI instantly
      setHistory(prev => prev.filter(item => item.id !== id));
      setSelectedIds(prev => prev.filter(sid => sid !== id)); // Deselect if selected
    } catch (error) {
      alert("Failed to delete receipt.");
    }
  };

  // ... (keep handleExport) ...
   const handleExport = async () => {
      if (selectedIds.length === 0) {
        alert("Please select at least one receipt to export.");
        return;
      }
  
      setIsExporting(true);
      try {
        const blob = await exportCSV(selectedIds);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `selected_expenses_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } catch (err) {
        alert("Export failed.");
      } finally {
        setIsExporting(false);
      }
    };

  // ... (keep Render logic) ...
  if (draftReceipt) {
      return (
        <DashboardLayout>
          <VerifyReceiptForm 
            initialData={draftReceipt}
            onCancel={() => setDraftReceipt(null)}
            onSuccess={() => {
              setDraftReceipt(null);
              fetchHistory(); // Refresh list after saving
              alert("Saved!");
            }}
          />
        </DashboardLayout>
      );
    }
  
    return (
      <DashboardLayout>
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold">Welcome, {username} 👋</h1>
            <p className="opacity-70">Here are your recent expenses.</p>
          </div>
          
          <div className="flex gap-3">
              <input type="file" hidden ref={fileInputRef} onChange={handleFileChange} accept="image/*"/>
              
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={isScanning}
                className="bg-blue-600 px-4 py-2 rounded-lg font-bold hover:bg-blue-700 transition"
              >
                {isScanning ? "Scanning..." : "+ New Receipt"}
              </button>
  
              <button 
                onClick={handleExport}
                disabled={isExporting || selectedIds.length === 0}
                className={`
                    px-4 py-2 rounded-lg font-bold transition flex items-center gap-2
                    ${selectedIds.length > 0 ? "bg-green-600 hover:bg-green-700 text-white" : "bg-white/10 text-white/40 cursor-not-allowed"}
                `}
              >
                {isExporting ? "Downloading..." : `Export (${selectedIds.length})`}
              </button>
  
              <button 
                onClick={() => {
                  localStorage.clear();
                  window.location.href = "/login";
                }}
                className="bg-red-500/10 text-red-200 border border-red-500/20 px-4 py-2 rounded-lg font-bold hover:bg-red-500/20 transition"
              >
                Sign Out
              </button>
          </div>
        </div>
  
        {scanError && <div className="text-red-400 mb-4">{scanError}</div>}
  
        {/* THE LIST (Pass handleDelete) */}
        <RecordsList 
          items={history} 
          selectedIds={selectedIds} 
          onToggle={toggleSelection}
          onDelete={handleDelete} // <--- Pass it here
        />
  
      </DashboardLayout>
    );
  }