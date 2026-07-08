/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Warm gold accent (matches the elegant academic look).
        brand: {
          50: "#faf6ec",
          100: "#f3e9cf",
          200: "#e7d29f",
          300: "#d9b866",
          400: "#cca33e",
          500: "#b8860b",
          600: "#9c7009",
          700: "#7d5a0b",
          800: "#67490f",
          900: "#573e11",
        },
        // Cream backgrounds.
        cream: {
          50: "#faf7f0",
          100: "#f3ede0",
          200: "#ece4d3",
          300: "#e2d7c0",
          400: "#d3c3a3",
        },
        ink: "#3d3527", // warm dark brown for text
      },
      fontFamily: {
        sans: ["Cairo", "Tajawal", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 10px 30px -12px rgba(90, 70, 20, 0.18)",
      },
    },
  },
  plugins: [],
};
