"use client";

type RecordItem = {
  id: number;
  total?: number;
  date?: string; // або date
  title?: string;
  shop?: string;
};

export default function RecordsList({
  items,
}: {
  items: RecordItem[];
}) {
  if (!items.length) {
    return (
      <div className="text-white/80 bg-white/10 border border-white/20 rounded-xl p-4">
        No records found.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {items.map((r) => (
        <div
          key={r.id}
          className="bg-white/10 border border-white/20 rounded-xl p-4 text-white"
        >
          <div className="flex justify-between gap-4">
            <div className="font-semibold">
              {r.title || r.shop || `Record #${r.id}`}
            </div>
            <div className="text-white/80">
              {typeof r.total === "number" ? `${r.total} €` : ""}
            </div>
          </div>

          <div className="text-sm text-white/70 mt-1">
            {r.date ? new Date(r.date).toLocaleString() : ""}
          </div>
        </div>
      ))}
    </div>
  );
}
