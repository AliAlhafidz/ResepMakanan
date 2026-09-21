/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./accounts/**/*.py",
    "./recipes/**/*.py",
    "./static/**/*.js"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
        serif: ['"Playfair Display"', 'serif'],
      },
      colors: {
        primary: {
          50: '#ecfdf3',
          100: '#d1fae1',
          200: '#a7f3c6',
          300: '#6ee7a3',
          400: '#34d37b',
          500: '#10b962',
          600: '#2E6A44',
          700: '#245336',
          800: '#1d422b',
          900: '#173623',
          950: '#0b1d12',
        },
        secondary: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#E5A93C',
          600: '#D97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        tertiary: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          500: '#ef4444',
          600: '#BA1A1A',
          700: '#991b1b',
          800: '#7f1d1d',
        },
        surface: {
          50: '#FDF8F5',
          100: '#F7EFEA',
          200: '#EFE3DC',
          300: '#DFCEC3',
          800: '#2E2825',
          900: '#1C1816',
        }
      },
      boxShadow: {
        'm3-1': '0px 1px 3px 1px rgba(0, 0, 0, 0.08), 0px 1px 2px 0px rgba(0, 0, 0, 0.12)',
        'm3-2': '0px 2px 6px 2px rgba(0, 0, 0, 0.08), 0px 1px 2px 0px rgba(0, 0, 0, 0.12)',
        'm3-3': '0px 4px 8px 3px rgba(0, 0, 0, 0.08), 0px 1px 3px 0px rgba(0, 0, 0, 0.12)',
      }
    }
  },
  plugins: [],
}
