module.exports = {
    content: ['./src/**/*.{html,js}', './node_modules/tw-elements/dist/js/**/*.js'],
    plugins: [
      require('tw-elements/dist/plugin'),
      require('@tailwindcss/typography'),
    ],
    theme: {
      container: {
        center: true,
        screens: {
          sm: '600px',
          md: '728px',
          lg: '984px',
          xl: '1240px',
          '2xl': '1496px',
        },
      },
      extend: { 
        colors: {
          dbn: {
            green: '#3E3E32',
            yellow: '#B1A569',
            yellowdark: '#7D744A',
            blue: '#96ADC8',
            red: '#EF3054',
            orange: '#c75000ff',
            purple: '#7F5A83'
          }
        }
      }
    }
  }