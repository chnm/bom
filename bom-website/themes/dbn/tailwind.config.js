/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["content/**/*.md", "layouts/**/*.html"],
  theme: {
    fontFamily: {
      display: "'Libre Caslon Display', serif",
      serif: "Spectral, serif",
      sans: "Spectral, serif",
      mono: "'IBM Plex Mono', monospace",
    },
    container: {
      center: true,
    },
    extend: {
      colors: {
        paper: {
          DEFAULT: '#f6f1e6',
          surface: '#fbf8f1',
          border: '#e0d8c6',
          'border-light': '#e8e1d1',
        },
        ink: {
          DEFAULT: '#24251f',
          muted: '#4a463c',
          body: '#56524a',
          faint: '#8a8474',
          caption: '#9a988a',
        },
        oxblood: {
          DEFAULT: '#9a3324',
          light: '#a8432e',
          dark: '#7d2b1f',
        },
        gold: '#b89150',
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
            50: '#fdf5f3',
            100: '#f9e8e4',
            200: '#f2cec6',
            300: '#e5a99c',
            400: '#d47d6b',
            500: '#be5a46',
            600: '#a8432e',
            700: '#9a3324',
            800: '#7d2b1f',
            900: '#68261e',
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
