/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#050315",
        "surface-dark": "#090620",
        "surface-card": "#0d092c",
        "surface-card-hover": "#130f3b",
        "surface-border": "#1f1a54",
        "surface-border-subtle": "rgba(222, 220, 255, 0.08)",
        primary: {
          DEFAULT: "#2f27ce",
          hover: "#261fa8",
          subtle: "rgba(47, 39, 206, 0.15)",
        },
        secondary: {
          DEFAULT: "#dedcff",
          muted: "#9b97db",
          dark: "#6b66b2",
        },
        accent: {
          DEFAULT: "#433bff",
          glow: "rgba(67, 59, 255, 0.25)",
          hover: "#3730e6",
        },
        status: {
          success: "#10b981",
          warning: "#f59e0b",
          error: "#ef4444",
          info: "#3b82f6",
          idle: "#64748b",
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'subtle-glow': '0 0 24px -4px rgba(67, 59, 255, 0.18)',
        'card-glow': '0 0 16px -2px rgba(47, 39, 206, 0.22)',
      },
      animation: {
        'pulse-subtle': 'pulse 2.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
