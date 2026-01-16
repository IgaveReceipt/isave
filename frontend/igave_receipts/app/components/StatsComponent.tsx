"use client";

import { useEffect, useMemo, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { apiGet } from "../services/api";
import { StatsData } from "../types";

// Cool Theme Colors (Purple, Pink, Blue, Teal, Orange)
const COLORS = ["#8884d8", "#ff8042", "#00C49F", "#FFBB28", "#ff4d4d"];

type Props = {
  /** Example: "today=true" | "date=2026-01-12" | "month=2026-01" | "year=2026" | "start=...&end=..." */
  query?: string;
};

export default function StatsComponent({ query = "" }: Props) {
  const [stats, setStats] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);

  const url = useMemo(() => {
    const q = query.trim();
    return q ? `/api/receipts/stats/?${q}` : "/api/receipts/stats/";
  }, [query]);

  useEffect(() => {
    let cancelled = false;

    const fetchStats = async () => {
      setLoading(true);
      try {
        const data = await apiGet<StatsData>(url);
        if (!cancelled) setStats(data);
      } catch (error) {
        console.error("Failed to fetch stats:", error);
        if (!cancelled) setStats(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchStats();

    return () => {
      cancelled = true;
    };
  }, [url]);

  if (loading) return <div className="p-4 text-white/50">Crunching the numbers...</div>;
  if (!stats || stats.total_spent === 0) return null;

  const chartData = stats.labels.map((label, index) => ({
    name: label,
    value: stats.data[index],
  }));

  return (
    <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6 mb-8 text-white shadow-xl">
      <div className="flex flex-col md:flex-row items-center justify-between">
        <div className="mb-6 md:mb-0 md:w-1/3">
          <h2 className="text-xl font-bold mb-2">The Accountant 📊</h2>
          <p className="text-white/60 text-sm mb-4">Breakdown of your expenses.</p>

          <div className="bg-white/5 rounded-lg p-4 inline-block">
            <p className="text-sm text-white/50 uppercase tracking-wider">Total Spent</p>
            <p className="text-3xl font-bold text-green-400">
              ${stats.total_spent.toFixed(2)}
            </p>
          </div>
        </div>

        <div className="w-full md:w-2/3">
  <ResponsiveContainer width="100%" height={256}>

            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: "#1a1a1a", border: "none", borderRadius: "8px" }}
                itemStyle={{ color: "#fff" }}
              />
              <Legend verticalAlign="bottom" height={36} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
