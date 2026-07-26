/** Build config for the compiled stylesheet.
    Run `npm run build:css` after changing markup or theme values. */
module.exports = {
  // js/site.js assembles status-message classes at runtime, so it must be
  // scanned too or those utilities get purged from the build.
  content: ['./*.html', './js/*.js'],
  theme: {
    extend: {
      colors: {
        navy:   '#0a2540',   // logo navy — primary brand and action colour
        ink:    '#06182b',   // deepest tone: utility bar and footer
        steel:  '#4a5c6f',   // body copy on light backgrounds
        sky:    '#2aa3e8',   // logo blue — accent only, used sparingly
        accent: '#12608f',   // deeper blue for hover and secondary emphasis
        mist:   '#f4f7fa',   // alternating section background
        line:   '#dde5ec',   // hairline borders
        skydk:  '#12608f',
        cloud:  '#f4f7fa',
      },
      fontFamily: {
        heading: ['"IBM Plex Sans"', 'sans-serif'],
        body:    ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
