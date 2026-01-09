"use client";

import { useEffect, useState } from "react";
import RecordsList from "../components/RecordsList";
import { apiGet } from "../services/api";

type ApiResponse = { results?: any[] } | any[];

export default function YearPage() {
  const [year, setYear] = useState(String(new Date().getFullYear()));
  const [items, setItems] = useState<any[]>([]);
  const [error, setError] = useState("");

  const load = async (y: string) => {
    try {
      setError("");
      const data = await apiGet<ApiResponse>(`/api/receipts/?year=${y}`);
      const arr = Array.isArray(data) ? data : (data.results ?? []);
      setItems(arr);
    } catch (e: any) {
      setError(e.message || "Failed to load");
      setItems([]);
    }
  };

  useEffect(() => {
    load(year);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-10">
      <div className="max-w-4xl mx-auto bg-white/10 border border-white/20 rounded-2xl p-8 backdrop-blur-xl">
        <div className="flex items-center justify-between gap-4 mb-6">
          <h1 className="text-3xl font-bold text-white">Year</h1>
          <div className="flex items-center gap-2">
            <input
              type="number"
              value={year}
              onChange={(e) => setYear(e.target.value)}
              className="w-28 rounded-lg px-3 py-2 bg-white/20 text-white border border-white/30"
              min="2000"
              max="2100"
            />
            <button
              onClick={() => load(year)}
              className="px-4 py-2 rounded-lg bg-white/30 hover:bg-white/40 text-white border border-white/20"
            >
              Load
            </button>
          </div>
        </div>

        {error && <div className="text-red-200 mb-4">{error}</div>}
        <RecordsList items={items} />
      </div>
    </div>
  );
}
