import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary brand colors (teal/green)
        primary: {
          DEFAULT: "#10b981", // Teal green
          dark: "#059669",    // Darker teal
          light: "#34d399",   // Lighter teal
        },

        // Accent color
        accent: {
          DEFAULT: "#10b981",
        },

        // Text colors
        text: {
          primary: "#111827",   // Nearly black (high contrast)
          secondary: "#4b5563", // Dark gray
          tertiary: "#9ca3af",  // Medium gray
        },

        // Background colors
        background: {
          DEFAULT: "#ffffff",
          elevated: "#fafafa",
          muted: "#f3f4f6",    // Light gray background
          dark: "#1f2937",     // Dark background
        },

        // Border colors
        border: {
          DEFAULT: "#e5e7eb",  // Light gray border
          accent: "#10b981",   // Primary color border
          dark: "#d1d5db",     // Slightly darker border
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
