/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: "#F7F7FB",
        ink: "#141A2E",
        slate: {
          DEFAULT: "#4B5468",
          light: "#7D8598",
        },
        brass: {
          DEFAULT: "#B8801F",
          light: "#E3A94A",
          dark: "#8F6317",
        },
        jacaranda: {
          DEFAULT: "#7C6BE0",
          light: "#B9AEF5",
          dark: "#5646B8",
        },
        line: "rgba(20, 26, 46, 0.10)",
        panel: "rgba(255, 255, 255, 0.62)",
      },
      fontFamily: {
        display: ["Bricolage Grotesque Variable", "Bricolage Grotesque", "ui-sans-serif", "system-ui", "-apple-system", "sans-serif"],
        body: ["Instrument Sans", "ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
      },
      borderRadius: {
        DEFAULT: "12px",
        sm: "8px",
        md: "14px",
        sheet: "28px",
      },
    },
  },
  plugins: [],
};
