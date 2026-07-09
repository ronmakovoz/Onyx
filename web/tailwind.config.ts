import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: "#161616",
        ink: "#2B2A26",
        muted: "#6E6A5C",
        faint: "#9C978A",
        line: "#EAE5D4",
        lavender: "#FBF4D8",
        chip: "#F7F3E4",
        red: "#C43D1B",
        amber: "#7A5C1E",
        green: "#2F9E55",
      },
      boxShadow: {
        card: "0 1px 4px rgba(22,22,22,0.05)",
        report: "0 10px 30px rgba(22,22,22,0.10), 0 2px 6px rgba(22,22,22,0.05)",
      },
    },
  },
  plugins: [],
};
export default config;
