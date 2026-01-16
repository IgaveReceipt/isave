"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link"; 
import VerifyReceiptForm from "../../components/VerifyReceiptForm";
import RecordsList, { ReceiptItem } from "../../components/RecordsList";
import StatsComponent from "../../components/StatsComponent"; 
import { scanReceipt, exportCSV, deleteReceipt, apiGet } from "../../services/api"; 
import { ReceiptData } from "../../types";

export default function DashboardPage() {
  const [username, setUsername] = useState("");
  // 1. Add state to hold staff status
  const [isStaff, setIsStaff] = useState(false); 

  const [history, setHistory] = useState<ReceiptItem[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [draftReceipt, setDraftReceipt] = useState<ReceiptData | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [scanError, setScanError] = useState("");
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const user = localStorage.getItem("username");
    // 2. Read the badge from storage
    const staffStatus = localStorage.getItem("is_staff");

    if (user) setUsername(user);
    // 3. Update state if they are staff
    if (staffStatus === "true") setIsStaff(true);

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

  const toggleSelection = (id: number) => {
      setSelectedIds(prev => 
        prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
      );
    };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this receipt?")) return;

    try {
      await deleteReceipt(id);
      setHistory(prev => prev.filter(item => item.id !== id));
      setSelectedIds(prev => prev.filter(sid => sid !== id)); 
    } catch (error) {
      alert("Failed to delete receipt.");
    }
  };

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

  // --- Render Logic ---
  if (draftReceipt) {
  return (
    <VerifyReceiptForm 
      initialData={draftReceipt}
      onCancel={() => setDraftReceipt(null)}
      onSuccess={() => {
        setDraftReceipt(null);
        fetchHistory(); 
        alert("Saved!");
      }}
    />
  );
}
  
    return (
  <>
    <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4 mb-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Welcome, {username} 👋</h1>
        <p className="text-white/70">Here are your recent expenses.</p>
      </div>

      <div className="flex flex-wrap gap-3">
        {isStaff && (
          <Link
            href="/users"
            className="bg-purple-600 px-4 py-2 rounded-lg font-bold hover:bg-purple-700 transition flex items-center shadow-lg border border-purple-400/30"
          >
            👥 Users
          </Link>
        )}

        <input type="file" hidden ref={fileInputRef} onChange={handleFileChange} accept="image/*" />

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

    <StatsComponent />

    <RecordsList
      items={history}
      selectedIds={selectedIds}
      onToggle={toggleSelection}
      onDelete={handleDelete}
    />
  </>
)};