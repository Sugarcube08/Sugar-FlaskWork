/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',    // Scan all HTML files in templates
    './static/js/**/*.js',      // Optional: Tailwind classes in JS
    './**/*.py'                 // Optional: Tailwind classes inside Python (Jinja templates)
  ],
  theme: {},
  plugins: [],
}

