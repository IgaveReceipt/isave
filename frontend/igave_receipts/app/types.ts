// This ensures we only use categories the backend understands
export enum Category {
  FOOD = "food",
  TRANSPORT = "transport",
  UTILITIES = "utilities",
  ENTERTAINMENT = "entertainment",
  OTHER = "other",
}

// This is the shape of the data we send to the backend
export interface ReceiptData {
  store_name: string;
  date: string;
  total_amount: number;
  category: Category;
  items?: string[]; // Optional list of items
}

export interface StatsData {
  labels: string[];
  data: number[];
  total_spent: number;
  filter: string;
}