/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        ink: '#1f2933',
        paper: '#f4efe6',
        panel: '#fffaf3',
        accent: '#9a3412',
        moss: '#557153',
        sand: '#caa76b',
        danger: '#b42318',
        muted: '#6b7280',
      },
      boxShadow: {
        soft: '0 20px 40px rgba(31, 41, 51, 0.08)',
      },
      fontFamily: {
        sans: ['Manrope', 'Segoe UI', 'sans-serif'],
        display: ['"Fraunces"', 'Georgia', 'serif'],
      },
      backgroundImage: {
        grain:
          'radial-gradient(circle at 1px 1px, rgba(154, 52, 18, 0.08) 1px, transparent 0)',
      },
    },
  },
  plugins: [],
}
