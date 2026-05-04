// API 服务层
// 后续接入真实API时修改此文件

// 如果页面没有引入 axios，先创建一个简单的请求工具
if (typeof axios === 'undefined') {
  window.axios = {
    create(options = {}) {
      const defaults = {
        baseURL: window.appConfig?.api?.baseURL || '',
        timeout: window.appConfig?.api?.timeout || 10000,
        headers: { 'Content-Type': 'application/json' }
      }
      const config = { ...defaults, ...options }

      const request = async (method, url, data = null) => {
        const fullUrl = config.baseURL + url
        try {
          const response = await fetch(fullUrl, {
            method,
            headers: config.headers,
            body: data ? JSON.stringify(data) : null
          })
          if (!response.ok) throw new Error(`HTTP ${response.status}`)
          return await response.json()
        } catch (error) {
          console.error(`API Error [${method} ${url}]:`, error)
          throw error
        }
      }

      return {
        get: (url) => request('GET', url),
        post: (url, data) => request('POST', url, data),
        put: (url, data) => request('PUT', url, data),
        delete: (url) => request('DELETE', url)
      }
    }
  }
}

// API 服务
window.apiService = {
  // 示例：弹幕相关（后续接入真实API）
  comments: {
    list: () => {
      if (window.appConfig.api.enableMock) {
        return Promise.resolve([
          { id: 1, user: '观众A', content: '好耶！', time: '12:30:45' },
          { id: 2, user: '观众B', content: '主播好棒', time: '12:31:20' }
        ])
      }
      return window.api.get('/comments')
    },
    send: (data) => {
      if (window.appConfig.api.enableMock) {
        return Promise.resolve({ success: true })
      }
      return window.api.post('/comments', data)
    }
  },

  // 示例：直播信息（后续接入真实API）
  live: {
    getInfo: () => {
      if (window.appConfig.api.enableMock) {
        return Promise.resolve({
          title: '日常直播',
          viewers: 666,
          status: 'live'
        })
      }
      return window.api.get('/live/info')
    },
    updateStatus: (status) => {
      return window.api.put('/live/status', { status })
    }
  }
}

// 初始化 API 实例
window.api = axios.create({
  baseURL: window.appConfig.api.baseURL,
  timeout: window.appConfig.api.timeout
})

// 请求拦截器
window.api.interceptors = {
  request: {
    use(onFulfilled, onRejected) {
      window.api._requestInterceptor = { onFulfilled, onRejected }
      return window.api
    }
  },
  response: {
    use(onFulfilled, onRejected) {
      window.api._responseInterceptor = { onFulfilled, onRejected }
      return window.api
    }
  }
}
