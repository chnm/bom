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
      screens: {
        sm: "600px",
        md: "728px",
        lg: "984px",
        xl: "1240px",
        "2xl": "1496px",
      },
    },
    extend: {
      colors: {
        dbn: {
          green: "#3E3E32",
          yellow: "#B1A569",
          yellowdark: "#7D744A",
          blue: "#96ADC8",
          red: "#EF3054",
          orange: "#c75000ff",
          purple: "#7F5A83",
        },
      },
    },
  },
  plugins: [
    require('postcss-import'),
    require('tw-elements/dist/plugin'),
    require('@tailwindcss/typography'),
  ],
};
