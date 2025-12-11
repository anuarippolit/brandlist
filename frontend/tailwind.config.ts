import type { Config } from 'tailwindcss';

export default {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      borderWidth: {
        3: '3px',
        1: '1px',
      },
      padding: {
        '0.25': '1px',
      },
      fontFamily: {
        poppins: ['Poppins', 'sans-serif'],
        inter: ['Inter', 'sans-serif'],
        bangers: ['"Bangers"', 'cursive'],
      },
      colors: {
        customPurple: '#6F00FF',
        inputColor: '#333333',
        darkgrayColor: '#171717',
        borderColor: 'rgba(255, 255, 255, 0.5)',
      },
      animation: {
        gallery: 'gallery 60s linear infinite',
        'slide-right': 'slide-right 10s linear infinite',
        'slide-left': 'slide-left 10s linear infinite',
      },
      keyframes: {
        gallery: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-100%)' },
        },
        'slide-right': {
          '0%': { transform: 'translateX(0%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        'slide-left': {
          '0%': { transform: 'translateX(0%)' },
          '100%': { transform: 'translateX(-100%)' },
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
