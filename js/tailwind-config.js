/* Tailwind Play CDN configuration — loaded after the CDN script on every page. */
tailwind.config = {
  theme: {
    extend: {
      colors: {
        navy:  '#0a2540',   // logo navy
        sky:   '#2aa3e8',   // logo blue
        skydk: '#1b86c4',   // hover blue
        cloud: '#f4f8fb',   // light section background
      },
      fontFamily: {
        heading: ['Poppins', 'sans-serif'],
        body:    ['Inter', 'sans-serif'],
      },
    },
  },
};
