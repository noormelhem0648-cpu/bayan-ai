/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef7f2",
          100: "#d6ece0",
          200: "#aedcc3",
          300: "#7cc59f",
          400: "#4aa878",
          500: "#2f8d5f",
          600: "#22714b",
          700: "#1d5a3e",
          800: "#194833",
          900: "#143b2b",
        },
      },
      fontFamily: {
        sans: ["Cairo", "Tajawal", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
