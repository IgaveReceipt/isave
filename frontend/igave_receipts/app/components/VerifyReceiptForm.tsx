"use client";

import { useState } from "react";
import { Category, ReceiptData } from "../types";
import { saveReceipt } from "../services/api";

interface Props {
  initialData: ReceiptData; // Data from the scanner
  onCancel: () => void;     // What to do if they click Cancel
  onSuccess: () => void;    // What to do after saving
}

export default function VerifyReceiptForm({ initialData, onCancel, onSuccess }: Props) {
  const [formData, setFormData] = useState<ReceiptData>(initialData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await saveReceipt(formData);
      onSuccess();
    } catch (err) {
      setError("Failed to save receipt. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md bg-white p-6 rounded-lg shadow-md border border-gray-200">
      <h2 className="text-xl font-bold mb-4 text-gray-800">Verify Receipt</h2>
      
      {error && <p className="text-red-500 text-sm mb-3">{error}</p>}

      <form onSubmit={handleSubmit} className="space-y-4">
        
        {/* Store Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Store / Vendor</label>
          <input
            name="store_name"
            value={formData.store_name}
            onChange={handleChange}
            className="w-full p-2 border rounded mt-1 focus:ring-2 focus:ring-blue-500 text-black"
            required
          />
        </div>

        {/* Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Date</label>
          <input
            type="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            className="w-full p-2 border rounded mt-1 text-black"
            required
          />
        </div>

        {/* Total Amount */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Total ($)</label>
          <input
            type="number"
            step="0.01"
            name="total_amount"
            value={formData.total_amount}
            onChange={handleChange}
            className="w-full p-2 border rounded mt-1 text-black"
            required
          />
        </div>

        {/* --- CATEGORIZATION DROPDOWN --- */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Category</label>
          <select
            name="category"
            value={formData.category}
            onChange={handleChange}
            className="w-full p-2 border rounded mt-1 bg-white text-black"
          >
            {Object.values(Category).map((cat) => (
              <option key={cat} value={cat}>
                {cat.toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        {/* Buttons */}
        <div className="flex gap-2 pt-2">
            <button
            type="button"
            onClick={onCancel}
            className="w-1/2 p-2 bg-gray-300 text-gray-800 rounded hover:bg-gray-400"
            >
            Cancel
            </button>
            <button
            type="submit"
            disabled={loading}
            className="w-1/2 p-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
            {loading ? "Saving..." : "Confirm & Save"}
            </button>
        </div>

      </form>
    </div>
  );
}