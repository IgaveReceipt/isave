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

export default function DayPage() {
  const [date, setDate] = useState(isoToday());
  const [items, setItems] = useState<any[]>([]);
  const [error, setError] = useState("");

  const load = async (d: string) => {
    try {
      setError("");
      const data = await apiGet<ApiResponse>(`/api/receipts/?date=${d}`);
      const arr = Array.isArray(data) ? data : (data.results ?? []);
      setItems(arr);
    } catch (e: any) {
      setError(e.message || "Failed to load");
      setItems([]);
    }
  };

  useEffect(() => {
    load(date);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <div className="flex items-center justify-between gap-4 mb-6">
        <h1 className="text-3xl font-bold text-white">Day</h1>

        <StatsComponent query={`date=${date}`} />


        <div className="flex items-center gap-2">
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="rounded-lg px-3 py-2 bg-white/20 text-white border border-white/30"
          />
          <button
            onClick={() => load(date)}
            className="px-4 py-2 rounded-lg bg-white/30 hover:bg-white/40 text-white border border-white/20"
          >
            Load
          </button>
        </div>
      </div>

      {error && <div className="text-red-200 mb-4">{error}</div>}
      <RecordsList items={items} />
    </>
  );
}
