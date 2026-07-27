import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        blinkit: {
          DEFAULT: "#F8CB46",
          dark: "#0B0B0B",
          muted: "#6B7280",
          green: "#318616",
          "green-dark": "#256812",
          ink: "#1A1A1A",
          surface: "#F8F8F8",
        },
      },
      boxShadow: {
        card: "0 1px 3px rgba(0,0,0,0.06)",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
