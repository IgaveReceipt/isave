"use client";

import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { apiGet } from "../services/api";
import { StatsData } from "../types";

// Cool Theme Colors (Purple, Pink, Blue, Teal, Orange)
const COLORS = ["#8884d8", "#ff8042", "#00C49F", "#FFBB28", "#ff4d4d"];

export default function StatsComponent() {
  const [stats, setStats] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      // By default, let's fetch "All Time" (no params). 
      // You can add ?month=X&year=Y here later if you want specific filters.
      const data = await apiGet<StatsData>("/api/receipts/stats/");
      setStats(data);
    } catch (error) {
      console.error("Failed to fetch stats:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-4 text-white/50">Crunching the numbers...</div>;
  if (!stats || stats.total_spent === 0) return null; // Don't show if empty

  // 🧠 THE GLUE: Transform Backend Arrays -> Recharts Objects
  const chartData = stats.labels.map((label, index) => ({
    name: label,
    value: stats.data[index],
  }));

  return (
    <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6 mb-8 text-white shadow-xl">
      <div className="flex flex-col md:flex-row items-center justify-between">
        
        {/* Left Side: Text Summary */}
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

        {/* Right Side: The Pie Chart */}
        <div className="w-full md:w-2/3 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60} // Donut style (modern look)
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: "#1a1a1a", border: "none", borderRadius: "8px" }}
                itemStyle={{ color: "#fff" }}
              />
              <Legend verticalAlign="bottom" height={36}/>
            </PieChart>
          </ResponsiveContainer>
        </div>

      </div>
    </div>
  );
}