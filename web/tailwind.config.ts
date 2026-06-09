import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: "#1B1040",
        ink: "#3D3458",
        muted: "#6B6280",
        faint: "#9B93A8",
        line: "#E8E4DC",
        lavender: "#F4EAF6",
        chip: "#F5F2EE",
        red: "#9B2335",
        amber: "#7A5C1E",
        green: "#2D5A3D",
      },
      boxShadow: {
        card: "0 1px 4px rgba(27,16,64,0.05)",
        report: "0 10px 30px rgba(27,16,64,0.10), 0 2px 6px rgba(27,16,64,0.05)",
      },
    },
  },
  plugins: [],
};
export default config;
