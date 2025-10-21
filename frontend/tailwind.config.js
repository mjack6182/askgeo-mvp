/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'parkside': {
          DEFAULT: '#006747',
          50: '#e6f2ed',
          100: '#ccf5e0',
          200: '#99ebc1',
          300: '#66e0a2',
          400: '#33d683',
          500: '#00cc64',
          600: '#006747',
          700: '#004d35',
          800: '#003323',
          900: '#001a12',
        },
      },
    },
  },
  plugins: [],
}
