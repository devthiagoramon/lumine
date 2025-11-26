import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para adicionar token e logar requisições
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // Log da requisição
    console.log('🌐 REQUEST:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL}${config.url}`,
      params: config.params,
      headers: config.headers
    })
    return config
  },
  (error) => {
    console.error('❌ REQUEST ERROR:', error)
    return Promise.reject(error)
  }
)

// Interceptor para tratar erros de autenticação e logar respostas
api.interceptors.response.use(
  (response) => {
    console.log('✅ RESPONSE:', {
      status: response.status,
      url: response.config.url,
      data: response.data
    })
    return response
  },
  (error) => {
    console.error('❌ RESPONSE ERROR:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      data: error.response?.data,
      request: error.request
    })
    
    if (error.response?.status === 401) {
      // Token expirado ou inválido
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
      // Redirecionar para login apenas se não estiver já na página de login
      if (window.location.pathname !== '/login' && window.location.pathname !== '/cadastro') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api

