/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#060606',
        accent: '#7C3AED',
        secondary: '#EC4899',
        highlight: '#FACC15',
        text: '#E5E7EB',
        healthy: '#EC4899',
        deploying: '#7C3AED',
        warning: '#FACC15',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Poppins', 'Inter', 'system-ui', 'sans-serif'],
      },
      letterSpacing: {
        tight: '-0.02em',
      },
      boxShadow: {
        'neon-grey': '0 0 10px rgba(96, 96, 96, 0.5), 0 0 20px rgba(96, 96, 96, 0.3)',
        'subtle-glow': '0 0 10px rgba(80, 80, 80, 0.3), 0 0 20px rgba(80, 80, 80, 0.2)',
      },
      animation: {
        'glow-pulse': 'glow-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'terminal-typing': 'terminal-typing 3s steps(40) infinite',
        'slide-up': 'slide-up 0.3s ease-out',
      },
      keyframes: {
        'glow-pulse': {
          '0%, 100%': { boxShadow: '0 0 10px rgba(96, 96, 96, 0.5), 0 0 20px rgba(96, 96, 96, 0.3)' },
          '50%': { boxShadow: '0 0 20px rgba(96, 96, 96, 0.8), 0 0 40px rgba(96, 96, 96, 0.5)' },
        },
        'terminal-typing': {
          '0%': { width: '0%' },
          '100%': { width: '100%' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}

