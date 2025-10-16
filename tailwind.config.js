module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        ttc: {
          red: '#DA020E',
          blue: '#003DA5',
          yellow: '#FFD100',
        }
      }
    },
  },
  plugins: [],
}
