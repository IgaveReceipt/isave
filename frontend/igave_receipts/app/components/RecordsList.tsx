"use client";

export type ReceiptItem = {
  id: number;
  store_name: string;
  total_amount: number;
  date: string;
  category: string;
};

type RecordsListProps = {
  items: ReceiptItem[];
  // 1. We make these OPTIONAL with the '?'
  selectedIds?: number[];
  onToggle?: (id: number) => void;
  onDelete?: (id: number) => void; 
};

// 2. We provide DEFAULTS in the function signature
export default function RecordsList({ 
  items, 
  selectedIds = [],      // Default: empty list (nothing selected)
  onToggle = () => {},   // Default: do nothing
  onDelete = () => {}    // Default: do nothing
}: RecordsListProps) {
  
  if (!items.length) {
    return (
      <div className="text-white/60 text-center py-8 bg-white/5 border border-white/10 rounded-xl">
        No scanned receipts found.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {items.map((r) => {
        const isSelected = selectedIds.includes(r.id);
        
        return (
          <div
            key={r.id}
            onClick={() => onToggle(r.id)} 
            className={`
              relative p-4 rounded-xl border cursor-pointer transition-all group flex justify-between items-center
              ${isSelected 
                ? "bg-blue-600/20 border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.3)]" 
                : "bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20"}
            `}
          >
            {/* LEFT SIDE: Checkbox + Info */}
            <div className="flex items-center gap-4">
              <div className={`
                w-5 h-5 rounded border flex items-center justify-center transition-colors
                ${isSelected ? "bg-blue-500 border-blue-500" : "border-white/30 bg-transparent"}
              `}>
                {isSelected && <span className="text-white text-xs">✓</span>}
              </div>

              <div>
                <div className="font-semibold text-white">
                  {r.store_name || "Unknown Store"}
                </div>
                <div className="text-xs text-white/60">
                  {r.date} • {r.category}
                </div>
              </div>
            </div>

            {/* RIGHT SIDE: Price + Delete Button */}
            <div className="flex items-center gap-4">
              <div className="font-bold text-lg text-white">
                {r.total_amount} €
              </div>
              
              {/* DELETE BUTTON (Trash Icon) */}
              <button
                onClick={(e) => {
                  e.stopPropagation(); // Stop clicking the row
                  onDelete(r.id);
                }}
                className="p-2 text-white/30 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition"
                title="Delete Receipt"
              >
                🗑️
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}