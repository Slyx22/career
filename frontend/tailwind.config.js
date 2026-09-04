/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: "#F4F6F4",
        ink: "#141A2E",
        slate: {
          DEFAULT: "#5B6472",
          light: "#8891A0",
        },
        brass: {
          DEFAULT: "#B8801F",
          light: "#E3A94A",
          dark: "#8F6317",
        },
        line: "#D8DCD6",
        panel: "#FFFFFF",
      },
      fontFamily: {
        display: ["Newsreader", "Georgia", "serif"],
        body: ["IBM Plex Sans", "Helvetica", "Arial", "sans-serif"],
      },
      borderRadius: {
        DEFAULT: "3px",
        sm: "2px",
        md: "4px",
      },
    },
  },
  plugins: [],
};
