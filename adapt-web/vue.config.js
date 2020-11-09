module.exports = {
  pages: {
    index: {
      // entry for the page
      entry: './src/pages/Home/main.js',
      // the source template
      template: 'public/index.html',
      // output as dist/index.html
      filename: 'index.html',
      // when using title option,
      // template title tag needs to be <title><%= htmlWebpackPlugin.options.title %></title>
      title: 'Home Page',
      // chunks to include on this page, by default includes
      // extracted common chunks and vendor chunks.
      chunks: ['chunk-vendors', 'chunk-common', 'index']
    },
    // when using the entry-only string format,
    // template is inferred to be `public/subpage.html`
    // and falls back to `public/index.html` if not found.
    // Output filename is inferred to be `subpage.html`.
    designs: {
      entry: './src/pages/Designs/main.js',
      template: 'public/index.html',
      filename: 'designs.html',
      title: 'Designs',
      chunks: ['chunk-vendors', 'chunk-common', 'designs']
    },
    adapt: {
      entry: './src/pages/ADAPT/main.js',
      template: 'public/index.html',
      filename: 'adapt.html',
      title: 'ADAPT',
      chunks: ['chunk-vendors', 'chunk-common', 'adapt']
    }
  }
}
