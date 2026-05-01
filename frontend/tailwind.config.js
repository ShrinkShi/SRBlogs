/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'Geist', 'ui-sans-serif', 'system-ui']
      },
      boxShadow: {
        glass: '0 24px 80px rgba(0, 0, 0, 0.35)'
      },
      backgroundImage: {
        'cyber-radial': 'radial-gradient(circle at 15% 10%, rgba(0,245,255,.32), transparent 30%), radial-gradient(circle at 85% 18%, rgba(168,85,247,.28), transparent 32%), radial-gradient(circle at 50% 90%, rgba(16,185,129,.18), transparent 35%)'
      }
    }
  },
  plugins: []
}
