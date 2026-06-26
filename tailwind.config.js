/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        'sb-navy': 'rgb(10, 54, 88)',      // Primary Deep Navy
        'sb-green': 'rgb(144, 191, 73)',   // Vibrant Brand Green
        'sb-teal': 'rgb(38, 102, 117)',    // Mid-Tone Teal
        'sb-neutral': 'rgb(248, 250, 252)', // Dashboard Neutral
      },
      backgroundImage: {
        'sb-gradient': 'linear-gradient(135deg, rgb(10, 54, 88) 0%, rgb(38, 102, 117) 100%)',
      }
    },
  },
  plugins: [],
}
