/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        bg: '#161616',
        panel: '#1E1E1E',
        surface: '#2c2c2c',
        border: '#3e3e3e',
        muted: '#8b8d91',
        accent: '#3ecf8e',
        success: '#3ecf8e',
        error: '#ff5b5b',
        warning: '#f5a623',
        info: '#4da6ff',
      }
    },
  },
  plugins: [],
}
