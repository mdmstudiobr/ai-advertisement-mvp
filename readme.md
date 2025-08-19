# 🚗 AI Car Ad Generator

## 🌟 Features
- **Multi-language car ads** (English, Spanish, Portuguese)
- **AI-powered content generation** using OpenAI or Ollama
- **Image enhancement** with OpenCV
- **Background removal** with transparent preview
- **Responsive web interface**

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key (optional, for OpenAI integration)

### Environment Setup

#### Option 1: Interactive Setup (Recommended)
```bash
cd api/
python setup_env.py
```

#### Option 2: Manual Setup
1. **Create `.env` file** in the `api/` directory:
```bash
cd api/
# Create .env file manually
```

2. **Configure your `.env` file**:
```env
# OpenAI API Configuration
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# AI Model Configuration
OPENAI_MODEL=gpt-4

# Ollama Configuration
OLLAMA_URL=http://ollama:11434/api/generate
MODEL_NAME=tinydolphin

# Default API Usage (True for OpenAI, False for Ollama)
USE_OPENAI_API=True
```

### Running the Project

1. **Start all services**:
```bash
docker-compose up -d
```

2. **Access the application**:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🏗️ Architecture

### Services
- **Frontend**: Vue.js 3 + Vite
- **Backend**: FastAPI (Python)
- **AI Service**: Ollama (local) + OpenAI (cloud)

### Key Components
- **`api/aiGenerator.py`**: AI content generation logic
- **`api/main.py`**: FastAPI backend with CORS
- **`api/setup_env.py`**: Environment configuration helper
- **`app/src/App.vue`**: Vue.js frontend interface
- **`docker-compose.yaml`**: Service orchestration

## 🔧 Configuration

### OpenAI vs Ollama
- **OpenAI**: Better quality, requires API key, costs money
- **Ollama**: Local, free, good quality with right models

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4)
- `USE_OPENAI_API`: Whether to use OpenAI (True) or Ollama (False)

## 📱 Usage

1. **Fill in car details** (make, model, year, km, fuel, transmission)
2. **Generate multi-language ad** with AI
3. **Enhance images** with OpenCV
4. **Remove backgrounds** with transparent preview

## 🛠️ Development

### Local Development
```bash
# Frontend
cd app/
npm install
npm run dev

# Backend
cd api/
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Building
```bash
# Frontend
cd app/
npm run build

# Backend
docker-compose up --build
```

## 🔒 Security Notes

- **Never commit API keys** to version control
- **Use `.env` files** for local development
- **Environment variables** are loaded securely in production
- **Run `setup_env.py`** to configure your environment safely

## 🐛 Troubleshooting

### Common Issues
1. **CORS errors**: Backend CORS is configured for localhost
2. **AI generation fails**: Check API key and model configuration
3. **Image processing errors**: Ensure OpenCV dependencies are installed

### Logs
```bash
# View logs
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 📄 License

This project is for educational and development purposes.
