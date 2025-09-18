<template>
  <div style="padding: 2rem; font-family: sans-serif;">
    <div style="width: 100%;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
        <h1>🚗 Motoreto: AI Car Ad Generator</h1>
        <div style="background: #007bff; color: white; padding: 0.5rem 1rem; border-radius: 4px; font-size: 0.9rem;">
          v2.5.3 - Vehicle Color Change Test (Any Vehicle → Metallic Blue)
        </div>
      </div>

      <form @submit.prevent="generateAd" style="display: flex; flex-wrap: wrap; gap: 1rem; width: 100%; align-items: flex-end;">
        <input v-model="form.make" placeholder="Make" required style="flex: 1 1 13%; min-width: 120px;" />
        <input v-model="form.model" placeholder="Model" required style="flex: 1 1 13%; min-width: 120px;" />
        <input v-model="form.year" placeholder="Year" required style="flex: 1 1 13%; min-width: 120px;" />
        <input v-model="form.km" placeholder="KM" required style="flex: 1 1 13%; min-width: 120px;" />
        <input v-model="form.fuel" placeholder="Fuel" required style="flex: 1 1 13%; min-width: 120px;" />
        <input v-model="form.transmission" placeholder="Transmission" required style="flex: 1 1 13%; min-width: 120px;" />
        <div style="flex-basis: 100%; display: flex; justify-content: flex-end; margin-top: 0.5rem;">
          <button type="submit">Generate Multi-Language Ad</button>
        </div>
      </form>

      <div v-if="loading">⏳ Generating ads in 3 languages...</div>

      <div v-if="result.en" style="margin-top: 2rem;">
        <h3 style="margin: 0 0 1rem 0; color: #007bff;">🇺🇸 English Version</h3>
        <div style="background: white; padding: 1rem; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
          <pre style="margin: 0; white-space: pre-wrap; font-family: inherit; color: #495057;">{{ result.en }}</pre>
        </div>
        
        <!-- Tags and Price -->
        <div v-if="result.tags || result.price" style="margin-top: 1rem; display: flex; gap: 1rem; flex-wrap: wrap;">
          <div v-if="result.tags" style="background: #e9ecef; padding: 0.5rem 1rem; border-radius: 4px;">
            <strong>🏷️ Tags:</strong> {{ result.tags }}
          </div>
          <div v-if="result.price" style="background: #d4edda; padding: 0.5rem 1rem; border-radius: 4px; color: #155724;">
            <strong>💰 Suggested Price:</strong> {{ result.price }}
          </div>
        </div>
      </div>

      <div v-if="result.es" style="margin-top: 2rem;">
        <h3 style="margin: 0 0 1rem 0; color: #28a745;">🇪🇸 Spanish Version</h3>
        <div style="background: white; padding: 1rem; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
          <pre style="margin: 0; white-space: pre-wrap; font-family: inherit; color: #495057;">{{ result.es }}</pre>
        </div>
      </div>

      <div v-if="result.pt" style="margin-top: 2rem;">
        <h3 style="margin: 0 0 1rem 0; color: #ffc107;">🇧🇷 Portuguese Version</h3>
        <div style="background: white; padding: 1rem; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
          <pre style="margin: 0; white-space: pre-wrap; font-family: inherit; color: #495057;">{{ result.pt }}</pre>
        </div>
      </div>
    </div>

    <div style="clear: both; margin-top: 2rem;">
      
      <div style="text-align: center; margin-top: 2rem;">
        <h2>🎨 Image Enhancement & 🖼️ Remove Background</h2>
        <label 
          for="image-upload" 
          style="
            display: inline-block;
            padding: 0.75rem 2rem;
            background: #007bff;
            color: #fff;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            font-size: 1rem;
            margin-top: 1rem;
            transition: background 0.2s;
          "
          @mouseover="handleMouseOver"
          @mouseleave="handleMouseLeave"
        >
          <span style="vertical-align: middle;">📁 Choose Image</span>
          <input 
            id="image-upload" 
            type="file" 
            @change="handleFile" 
            accept="image/*" 
            style="display: none;"
          />
        </label>
      </div>

      <div v-if="enhancedImage || image" style="margin-top: 1rem;">
        <h3>Result:</h3>
        <div style="display: flex; gap: 2rem; align-items: flex-start; flex-wrap: wrap;">
          <!-- Coluna 1: Imagem Original -->
          <div style="text-align: center; flex: 1 1 0;">
            <h4 style="margin: 0 0 0.5rem 0; color: #666;">📷 Original</h4>
            <img v-if="originalImageUrl" :src="originalImageUrl" alt="Original" style="max-width: 300px; border: 2px solid #ddd; border-radius: 8px;" />
          </div>
          <!-- Coluna 2: Imagem Enhanced (Python) -->
          <div style="text-align: center; flex: 1 1 0;">
            <h4 style="margin: 0 0 0.5rem 0; color: #007bff;">✨ Enhanced (Python)</h4>
            <img v-if="enhancedImage" :src="enhancedImage" alt="Enhanced" style="max-width: 300px; border: 2px solid #007bff; border-radius: 8px;" />
          </div>
          <!-- Coluna 3: Imagem Enhanced (Replicate) -->
          <div style="text-align: center; flex: 1 1 0;">
            <h4 style="margin: 0 0 0.5rem 0; color: #9c27b0;">🎨 New Color (Replicate)</h4>
            <button @click="enhanceImageReplicate" :disabled="!file || replicateLoading" style="margin-bottom: 0.5rem;">
              {{ replicateLoading ? '🔄 Processing...' : '🎨 Replicate Enhancement' }}
            </button>
            <img v-if="enhancedImageReplicate" :src="enhancedImageReplicate" alt="Replicate Enhanced" style="max-width: 300px; border: 2px solid #9c27b0; border-radius: 8px;" />
            <div v-if="!enhancedImageReplicate" style="min-height: 200px; border: 2px dashed #9c27b0; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #9c27b0;">
              <span>Click "Replicate Enhancement" to process</span>
            </div>
          </div>
          <!-- Coluna 5: Imagem sem fundo -->
          <div style="text-align: center; flex: 1 1 0;">
            <h4 style="margin: 0 0 0.5rem 0; color: #ffc107;">🖼️ No Background</h4>
            <button @click="removeBg" :disabled="!file" style="margin-bottom: 0.5rem;">Remove Background</button>
            <div v-if="image"
              :style="{ 
                background: `linear-gradient(45deg, ${transparentBgColor} 25%, transparent 25%), linear-gradient(-45deg, ${transparentBgColor} 25%, transparent 25%), linear-gradient(45deg, transparent 75%, ${transparentBgColor} 75%), linear-gradient(-45deg, transparent 75%, ${transparentBgColor} 75%)`,
                backgroundSize: '20px 20px',
                backgroundPosition: '0 0, 0 10px, 10px -10px, -10px 0px',
                padding: '10px',
                borderRadius: '8px',
                display: 'inline-block',
                cursor: 'pointer'
              }"
              @click="changeBgColor"
              title="Click to change background color"
            >
              <img :src="image" alt="Processed" style="max-width: 300px; display: block;" />
            </div>
            <p v-if="image" style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">
              Background: {{ transparentBgColor }} (click to change)
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import { getApiUrl, API_CONFIG } from './config.js'

const form = ref({
  make: '',
  model: '',
  year: '',
  km: '',
  fuel: '',
  transmission: ''
})

const result = ref('')
const loading = ref(false)
const file = ref(null)
const image = ref(null)
const enhancedImage = ref(null)
const enhancedImageOpenAI = ref(null)
const enhancedImageReplicate = ref(null)
const originalImageUrl = ref(null)
const transparentBgColor = ref('#ff6b6b')
const openaiLoading = ref(false)
const replicateLoading = ref(false)

// Generate random color for transparent background
function generateRandomColor() {
  const colors = [
    '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57',
    '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff9f43',
    '#ff7675', '#74b9ff', '#a29bfe', '#fd79a8', '#fdcb6e'
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}

// Mouseover handlers for the upload button
function handleMouseOver(event) {
  if (event && event.target) {
    event.target.style.background = '#0056b3'
  }
}

function handleMouseLeave(event) {
  if (event && event.target) {
    event.target.style.background = '#007bff'
  }
}

// Change background color
function changeBgColor() {
  transparentBgColor.value = generateRandomColor()
}

onMounted(() => {
  // Generate initial color
  transparentBgColor.value = generateRandomColor()
})

async function generateAd() {
  if (!form.value.make || !form.value.model || !form.value.year) {
    alert('Por favor, preencha marca, modelo e ano')
    return
  }

  loading.value = true
  result.value = ''

  try {
    console.log('🚀 Gerando anúncio multi-idioma...')
    
    // Use the default aiGenerator prompt (no custom prompt)
    const response = await axios.post(getApiUrl(API_CONFIG.ENDPOINTS.GENERATE_AD), {
      ...form.value
    })

    console.log('✅ Anúncio gerado:', response.data)
    
    // Use the response directly from aiGenerator (it already includes all 3 languages)
    if (response.data.error) {
      throw new Error(`AI Error: ${response.data.error} - ${response.data.raw || ''}`)
    }
    
    if (!response.data.advertisement || !response.data.advertisement.english) {
      throw new Error('Resposta inválida da IA. Tente novamente com dados válidos.')
    }
    
    result.value = {
      en: response.data.advertisement.english,
      es: response.data.advertisement.spanish,
      pt: response.data.advertisement.brazilian_portuguese,
      tags: response.data.tags,
      price: response.data.suggested_reseller_price
    }

    console.log('🎉 Anúncios em todos os idiomas:', result.value)

  } catch (err) {
    console.error('❌ Erro ao gerar anúncio:', err)
    alert('Erro ao gerar anúncio: ' + err.message)
  } finally {
    loading.value = false
  }
}

async function handleFile(e) {
  file.value = e.target.files[0]
  if (!file.value) return

  // Criar URL para a imagem original
  originalImageUrl.value = URL.createObjectURL(file.value)

  const formData = new FormData()
  formData.append('file', file.value)

  try {
    console.log('🔄 Enviando imagem para enhancement...')
    
    // Para enhancement, o backend retorna a imagem diretamente
    const res = await axios.post(getApiUrl(API_CONFIG.ENDPOINTS.ENHANCE_IMAGE), formData, {
      responseType: 'blob'
    })
    
    console.log('✅ Resposta recebida:', res.data)
    console.log('📊 Tipo da resposta:', typeof res.data)
    console.log('📏 Tamanho da resposta:', res.data.size)
    
    // Criar URL para a imagem enhanced
    enhancedImage.value = URL.createObjectURL(res.data)
    console.log('🖼️ Imagem enhanced criada com sucesso')
    
  } catch (err) {
    console.error('❌ Erro ao processar imagem:', err)
    alert('Erro ao processar imagem: ' + err.message)
  }
}

async function enhanceImageReplicate() {
  if (!file.value) return alert("Please upload an image first")
  
  replicateLoading.value = true
  const formData = new FormData()
  formData.append('file', file.value)

  try {
    console.log('🚀 Enviando imagem para Replicate enhancement...')
    console.log('📁 Arquivo:', file.value.name, 'Tamanho:', file.value.size)
    
    // Replicate enhancement returns image directly
    const res = await axios.post(getApiUrl(API_CONFIG.ENDPOINTS.ENHANCE_IMAGE_REPLICATE), formData, {
      responseType: 'blob'
    })
    
    console.log('✅ Replicate enhancement concluído')
    console.log('📊 Resposta:', res.data)
    console.log('📏 Tamanho da resposta:', res.data.size)
    console.log('🔗 Tipo da resposta:', res.data.type)
    
    // Create URL for Replicate enhanced image
    enhancedImageReplicate.value = URL.createObjectURL(res.data)
    console.log('🖼️ Imagem Replicate enhanced criada com sucesso')
    console.log('🔗 URL criada:', enhancedImageReplicate.value)
    
    // Force Vue to re-render
    await nextTick()
    
  } catch (err) {
    console.error('❌ Erro no Replicate enhancement:', err)
    if (err.response && err.response.data) {
      // Try to read error message from blob response
      try {
        const errorText = await err.response.data.text()
        console.error('📝 Erro do servidor:', errorText)
        alert('Erro no Replicate enhancement: ' + errorText)
      } catch (textError) {
        console.error('📝 Erro ao ler resposta de erro:', textError)
        alert('Erro no Replicate enhancement: ' + err.message)
      }
    } else {
      alert('Erro no Replicate enhancement: ' + err.message)
    }
  } finally {
    replicateLoading.value = false
  }
}

async function removeBg() {
  if (!file.value) return alert("Please upload an image first")
  
  const formData = new FormData()
  formData.append('file', file.value)

  try {
    console.log('🔄 Enviando imagem para remoção de fundo...')
    
    // Para remove-bg, o backend retorna JSON com hex
    const res = await axios.post(getApiUrl(API_CONFIG.ENDPOINTS.REMOVE_BG), formData)
    
    console.log('✅ Resposta recebida:', res.data)
    
    if (res.data.image) {
      // Converter hex para base64
      image.value = "data:image/png;base64," + hexToBase64(res.data.image)
      console.log('🖼️ Imagem sem fundo criada com sucesso')
      
      // Generate new color for background
      transparentBgColor.value = generateRandomColor()
    } else {
      throw new Error('Resposta inválida do servidor')
    }
  } catch (err) {
    console.error('❌ Erro ao remover fundo:', err)
    alert('Erro ao remover fundo: ' + err.message)
  }
}

function hexToBase64(hex) {
  try {
    console.log('🔄 Convertendo hex para base64...')
    console.log('📝 Hex recebido:', hex)
    
    if (!hex || typeof hex !== 'string') {
      throw new Error('Hex inválido ou não fornecido')
    }
    
    const bytes = new Uint8Array(hex.match(/.{1,2}/g).map(byte => parseInt(byte, 16)))
    let binary = ''
    bytes.forEach(b => binary += String.fromCharCode(b))
    const result = btoa(binary)
    
    console.log('✅ Conversão concluída')
    return result
  } catch (err) {
    console.error('❌ Erro ao converter hex para base64:', err)
    return ''
  }
}
</script>

<style scoped>
input {
  display: block;
  margin: 0.5rem 0;
  padding: 0.5rem;
  width: 100%;
  max-width: 300px;
}

button {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  margin: 0.5rem 0;
  cursor: pointer;
  border-radius: 4px;
}

button:hover {
  background: #0056b3;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

pre {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  white-space: pre-wrap;
}

/* Style for transparent background */
.transparent-bg {
  cursor: pointer;
  transition: all 0.3s ease;
}

.transparent-bg:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
</style>