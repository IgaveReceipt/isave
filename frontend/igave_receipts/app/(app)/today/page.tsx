"use client";

import { useEffect, useState } from "react";
import RecordsList from "../../components/RecordsList";
import { apiGet } from "../../services/api";
import StatsComponent from "../../components/StatsComponent";


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
  <>
    <h1 className="text-3xl font-bold text-white mb-6">Today</h1>
    {error && <div className="text-red-200 mb-4">{error}</div>}

    <StatsComponent query="today=true" />

    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
      <RecordsList items={items} />
    </div>
  </>
);
}
