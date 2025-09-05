//frontend\postcss.config.cjs
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {
      config: './tailwind.config.cjs'
    },
    autoprefixer: {},
  }
}