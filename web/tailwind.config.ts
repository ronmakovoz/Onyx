import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: "#0E1E45",
        ink: "#2E3A56",
        muted: "#64718C",
        faint: "#93A0B8",
        line: "#E3E8F0",
        lavender: "#EAF0FB",
        chip: "#F2F5F9",
        red: "#9B2335",
        amber: "#7A5C1E",
        green: "#1F6B4A",
      },
      boxShadow: {
        card: "0 1px 4px rgba(14,30,69,0.05)",
        report: "0 10px 30px rgba(14,30,69,0.10), 0 2px 6px rgba(14,30,69,0.05)",
      },
    },
  },
  plugins: [],
};
export default config;
