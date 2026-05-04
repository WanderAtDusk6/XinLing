// 全局配置文件
// 修改配置只需编辑此文件

window.appConfig = {
  // 轮播设置
  carousel: {
    autoPlay: true,
    interval: 8000,
    pauseOnHover: false
  },

  // API 配置（后续接入API时修改这里）
  api: {
    baseURL: 'https://api.example.com',
    timeout: 10000,
    enableMock: true
  },

  // 评论区域设置
  comment: {
    refreshInterval: 5000,
    maxCount: 100
  },

  // 屏幕共享设置
  screenShare: {
    video: {
      cursor: 'always',
      displaySurface: 'monitor'
    },
    audio: false
  }
}
