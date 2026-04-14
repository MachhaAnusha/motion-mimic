/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'graffiti-black': '#0a0a0a',
        'graffiti-charcoal': '#1a1a1a',
        'graffiti-neon': '#39ff14',
        'graffiti-electric': '#00d4ff',
        'graffiti-hot': '#ff1493',
        'graffiti-fire': '#ff4500',
        'graffiti-chrome': '#c0c0c0',
      },
      fontFamily: {
        'graffiti': ['Boogaloo', 'cursive'],
        'marker': ['Permanent Marker', 'cursive'],
        'dirt': ['Rubik Dirt', 'cursive'],
      },
      animation: {
        'spray': 'spray 0.3s ease-out',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        spray: {
          '0%': { opacity: '0', transform: 'scale(0.8)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        glow: {
          '0%': { filter: 'drop-shadow(0 0 5px currentColor)' },
          '100%': { filter: 'drop-shadow(0 0 20px currentColor) drop-shadow(0 0 40px currentColor)' },
        },
      },
    },
  },
  plugins: [],
}
