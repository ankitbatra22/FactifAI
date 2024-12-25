/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)'],
        'plus-jakarta': ['var(--font-plus-jakarta)'],
      },
      colors: {
        dark: {
          900: '#0D1117',
          800: '#1C1F26',
          700: '#2D3139',
        },
      },
    },
  },
  plugins: [],
}