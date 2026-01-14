/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
        colors: {
            primary: '#3b82f6',
            secondary: '#64748b',
            success: '#10b981',
            danger: '#ef4444',
            warning: '#f59e0b',
            info: '#06b6d4',
            light: '#f8fafc',
            dark: '#1e293b'
        },
        fontFamily: {
            sans: ['Inter', 'system-ui', 'sans-serif'],
        },
        animation: {
            'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        }
    },
  },
  plugins: [],
}
