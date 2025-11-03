/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["content/**/*.md", "layouts/**/*.html"],
  theme: {
    fontFamily: {
      serif: "Libre Baskerville, Playfair Display, serif",
      sans: "Work Sans, sans-serif",
    },
    container: {
      center: true,
    },
    extend: {
      colors: {
        dbn: {
          green: {
            50: '#f6f7f4',
            100: '#e8eae4',
            200: '#d1d6c8',
            300: '#b3bca7',
            400: '#8f9d80',
            500: '#5a5d4f',
            600: '#4a4d40',
            700: '#3d3f35',
            800: '#32342b',
            900: '#3E3E32',
          },
          yellow: {
            50: '#fdfcf7',
            100: '#f7f4e8',
            200: '#ede7c8',
            300: '#dfd49f',
            400: '#B1A569',
            500: '#9d8f5c',
            600: '#8a7d4f',
            700: '#7D744A',
            800: '#655c3c',
            900: '#4d4530',
          },
          blue: {
            50: '#f0f4f8',
            100: '#d9e2ec',
            200: '#bcccdc',
            300: '#9fb3c8',
            400: '#7BA7C7',
            500: '#6b9dc2',
            600: '#5a8bb5',
            700: '#4a73a0',
            800: '#3c5d82',
            900: '#2d4563',
          },
          red: {
            50: '#fef2f2',
            100: '#fee2e2',
            200: '#fecaca',
            300: '#fca5a5',
            400: '#f87171',
            500: '#E63946',
            600: '#dc2626',
            700: '#b91c1c',
            800: '#991b1b',
            900: '#7f1d1d',
          },
          orange: {
            50: '#fff7ed',
            100: '#ffedd5',
            200: '#fed7aa',
            300: '#fdba74',
            400: '#F77F00',
            500: '#ea580c',
            600: '#dc2626',
            700: '#c2410c',
            800: '#9a3412',
            900: '#7c2d12',
          },
          purple: {
            50: '#faf5ff',
            100: '#f3e8ff',
            200: '#e9d5ff',
            300: '#d8b4fe',
            400: '#c084fc',
            500: '#8B5A83',
            600: '#7c3aed',
            700: '#6d28d9',
            800: '#5b21b6',
            900: '#4c1d95',
          },
        },
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: "82ch",
          }
        }
      },
    },
  },
  plugins: [
    require('postcss-import'),
    require('tw-elements/dist/plugin'),
    require('@tailwindcss/typography'),
  ],
};
