const MomentLocalesPlugin = require("moment-locales-webpack-plugin");

module.exports = {
  productionSourceMap: false,
  publicPath: process.env.VUE_APP_ROOT,
  configureWebpack: {
    plugins: [
      new MomentLocalesPlugin({
        localesToKeep: ["zh-CN"]
      })
    ],
    devtool: 'source-map'
  }
};
