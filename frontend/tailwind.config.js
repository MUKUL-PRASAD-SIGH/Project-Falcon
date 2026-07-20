/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#070D18',
          900: '#0B1526',
          800: '#101E36',
          700: '#182A48'
        },
        panel: '#131F38',
        border: '#24344F',
        gold: {
          DEFAULT: '#C9A227',
          bright: '#E4C452'
        },
        khaki: '#A98E5C',
        alert: '#D8503A',
        ink: {
          DEFAULT: '#E8E6DD',
          dim: '#93A0B8'
        }
      },
      fontFamily: {
        /* Plus Jakarta Sans — modern, crisp, professional display font */
        display: ['"Plus Jakarta Sans"', 'sans-serif'],
        /* Inter — the industry standard clean body font */
        body: ['Inter', 'sans-serif'],
        /* IBM Plex Mono — evidence numbers & timestamps */
        mono: ['"IBM Plex Mono"', 'monospace']
      }
    }
  },
  plugins: []
}
