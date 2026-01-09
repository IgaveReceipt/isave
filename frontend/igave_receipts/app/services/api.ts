import { ReceiptData } from "../types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function login(body: {
  username: string;
  password: string;
}) {
  const res = await fetch(`${API_BASE_URL}/api/login/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw new Error("Login failed");
  }

  return res.json();
}

export const scanReceipt = async (file: File) => {
  const token = localStorage.getItem("access"); // Get the token
  const formData = new FormData();
  formData.append("file", file);

  // We append "/api" to match your existing URL structure
  const response = await fetch(`${API_BASE_URL}/api/receipts/scan/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) throw new Error("Scan failed");
  return response.json();
};

export const saveReceipt = async (data: ReceiptData) => {
  const token = localStorage.getItem("access");
  
  const response = await fetch(`${API_BASE_URL}/api/receipts/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) throw new Error("Failed to save receipt");
  return response.json();
};
