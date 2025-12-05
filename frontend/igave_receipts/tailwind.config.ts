import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "dark-start": "#111111",
        "dark-mid": "#000000",
        "dark-end": "#1a1a1a",
      },
    },
  },
} satisfies Config;

