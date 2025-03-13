module.exports = {
    devServer: {
      proxy: {
        "/api": {
          target: "http://127.0.0.1:5000", // Flask 后端地址
          changeOrigin: true,
          pathRewrite: { "^/api": "" },
        },
      },
    },
  };