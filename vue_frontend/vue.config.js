const BundleTracker = require("webpack-bundle-tracker")

const pages =  {
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
  runadapt: {
    entry: './src/pages/RunADAPT/main.js',
    template: 'public/index.html',
    filename: 'runadapt.html',
    title: 'Run ADAPT',
    chunks: ['chunk-vendors', 'chunk-common', 'runadapt']
  },
  results: {
    entry: './src/pages/Results/main.js',
    template: 'public/index.html',
    filename: 'results.html',
    title: 'View Results',
    chunks: ['chunk-vendors', 'chunk-common', 'results']
  }
}

module.exports = {
  pages: pages,
  filenameHashing: false,
  productionSourceMap: false,
  publicPath: process.env.NODE_ENV === 'production'
    ? ''
    : 'http://localhost:8080/',
  outputDir: '../static/vue/',

  chainWebpack: config => {

    config.optimization
      .splitChunks({
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: "chunk-vendors",
            chunks: "all",
            priority: 1
          },
        },
      });

    Object.keys(pages).forEach(page => {
      config.plugins.delete(`html-${page}`);
      config.plugins.delete(`preload-${page}`);
      config.plugins.delete(`prefetch-${page}`);
    })

    config
      .plugin('BundleTracker')
      .use(BundleTracker, [{filename: './webpack-stats.json'}]);

    config.resolve.alias
        .set('__STATIC__', 'static')

    config.devServer
        .public('http://localhost:8080')
        .host('localhost')
        .port(8080)
        .hotOnly(true)
        .watchOptions({poll: 1000})
        .https(false)
        .headers({"Access-Control-Allow-Origin": ["*"]})

  }
}
