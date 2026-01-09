import { ReceiptData } from "../types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

function getAccessToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access");
}

export async function apiGet<T>(path: string): Promise<T> {
  const token = getAccessToken();

  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    cache: "no-store",
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const msg = data?.detail || `Request failed: ${res.status}`;
    throw new Error(msg);
  }

  return data as T;
}

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
