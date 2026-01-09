"use client";

import { useEffect, useState } from "react";
import RecordsList from "../components/RecordsList";
import { apiGet } from "../services/api";

type ApiResponse = { results?: any[] } | any[];

export default function TodayPage() {
  const [items, setItems] = useState<any[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        setError("");
        const data = await apiGet<ApiResponse>("/api/receipts/?today=true");
        const arr = Array.isArray(data) ? data : (data.results ?? []);
        setItems(arr);
      } catch (e: any) {
        setError(e.message || "Failed to load");
      }
    };
    load();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-10">
      <div className="max-w-4xl mx-auto bg-white/10 border border-white/20 rounded-2xl p-8 backdrop-blur-xl">
        <h1 className="text-3xl font-bold text-white mb-6">Today</h1>
        {error && <div className="text-red-200 mb-4">{error}</div>}
        <RecordsList items={items} />
      </div>
    </div>
  );
}
