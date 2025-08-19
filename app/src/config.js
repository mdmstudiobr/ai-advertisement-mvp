// Configuração da API
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',
  ENDPOINTS: {
    GENERATE_AD: '/generate-ad',
    ENHANCE_IMAGE: '/enhance-image',
    ENHANCE_IMAGE_OPENAI: '/enhance-image-openai',
    ENHANCE_IMAGE_REPLICATE: '/enhance-image-replicate',
    REMOVE_BG: '/remove-bg'
  }
}

// Função para construir URLs completas
export function getApiUrl(endpoint) {
  return `${API_CONFIG.BASE_URL}${endpoint}`
}
