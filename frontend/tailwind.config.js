/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: { DEFAULT: '#0F172A', soft: '#475569', faint: '#94A3B8' },
        ledger: { DEFAULT: '#2563EB', deep: '#1D4ED8', indigo: '#4F46E5' },
        paper: { DEFAULT: '#FFFFFF', bg: '#F8FAFC' },
        ok: '#16A34A',
        warn: '#F59E0B',
        bad: '#DC2626',
      },
      fontFamily: {
        sans: ['"PingFang SC"', '"Helvetica Neue"', 'Arial', 'sans-serif'],
        mont: ['Montserrat', '"PingFang SC"', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 2px rgba(15,23,42,.05), 0 8px 24px -12px rgba(37,99,235,.18)',
        lift: '0 2px 4px rgba(15,23,42,.06), 0 16px 40px -16px rgba(37,99,235,.30)',
      },
      keyframes: {
        rise: {
          from: { opacity: '0', transform: 'translateY(12px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: { rise: 'rise .45s cubic-bezier(.22,1,.36,1) both' },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
