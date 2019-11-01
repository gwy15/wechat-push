const MomentLocalesPlugin = require("moment-locales-webpack-plugin");

module.exports = {
  productionSourceMap: false,
  configureWebpack: {
    plugins: [
      new MomentLocalesPlugin({
        localesToKeep: ["zh-CN"]
      })
    ]
  }
};
