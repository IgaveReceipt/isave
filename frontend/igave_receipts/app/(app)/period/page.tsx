"use client";

import { useEffect, useState } from "react";
import RecordsList from "../../components/RecordsList";
import { apiGet } from "../../services/api";
import StatsComponent from "../../components/StatsComponent";


type ApiResponse = { results?: any[] } | any[];

function isoToday() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

export default function PeriodPage() {
  const today = isoToday();
  const [start, setStart] = useState(today);
  const [end, setEnd] = useState(today);
  const [items, setItems] = useState<any[]>([]);
  const [error, setError] = useState("");

  const load = async (s: string, e: string) => {
    try {
      setError("");
      const data = await apiGet<ApiResponse>(`/api/receipts/?start=${s}&end=${e}`);
      const arr = Array.isArray(data) ? data : (data.results ?? []);
      setItems(arr);
    } catch (err: any) {
      setError(err.message || "Failed to load");
      setItems([]);
    }
  };

  const DEMO_MODE = true;

const demo = [
  { id: 1, title: "Demo receipt", total: 12.5, created_at: new Date().toISOString() },
  { id: 2, title: "Demo receipt 2", total: 7.99, created_at: new Date().toISOString() },
];


useEffect(() => {
  if (DEMO_MODE) {
    setItems(demo);
    return;
  }
  load(start, end); 
}, [start, end]);


  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-10">
      <div className="max-w-4xl mx-auto bg-white/10 border border-white/20 rounded-2xl p-8 backdrop-blur-xl">
        <div className="flex items-center justify-between gap-4 mb-6">
          <h1 className="text-3xl font-bold text-white">Period</h1>

          <StatsComponent query={`start=${start}&end=${end}`} />


          <div className="flex flex-wrap items-center gap-2">
            <input
              type="date"
              value={start}
              onChange={(e) => setStart(e.target.value)}
              className="rounded-lg px-3 py-2 bg-white/20 text-white border border-white/30"
            />
            <input
              type="date"
              value={end}
              onChange={(e) => setEnd(e.target.value)}
              className="rounded-lg px-3 py-2 bg-white/20 text-white border border-white/30"
            />
            <button
              onClick={() => load(start, end)}
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
