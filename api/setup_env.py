#!/usr/bin/env python3
"""
Environment Setup Script for AI Car Ad Generator
This script helps you create a .env file with your configuration.
"""

import os
import sys

def create_env_file():
    """Create .env file with user input"""
    
    print("🚗 AI Car Ad Generator - Environment Setup")
    print("=" * 50)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    # Get OpenAI API key
    print("\n🔑 OpenAI Configuration:")
    print("Get your API key from: https://platform.openai.com/api-keys")
    openai_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    # Get model preference
    openai_model = input("Enter OpenAI model (default: gpt-4): ").strip() or "gpt-4"
    
    # Get Ollama configuration
    print("\n🤖 Ollama Configuration:")
    ollama_url = input("Enter Ollama URL (default: http://ollama:11434/api/generate): ").strip() or "http://ollama:11434/api/generate"
    model_name = input("Enter model name (default: tinydolphin): ").strip() or "tinydolphin"
    
    # Get Replicate configuration
    print("\n🤖 Replicate Configuration:")
    print("Get your API token from: https://replicate.com/account/api-tokens")
    replicate_token = input("Enter your Replicate API token: ").strip()
    
    # Get API preference
    print("\n⚙️  API Configuration:")
    use_openai = input("Use OpenAI API? (Y/n): ").lower()
    use_openai = "True" if use_openai != "n" else "False"
    
    # Create .env content
    env_content = f"""# OpenAI API Configuration
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY={openai_key}

# AI Model Configuration
OPENAI_MODEL={openai_model}

# Ollama Configuration
OLLAMA_URL={ollama_url}
MODEL_NAME={model_name}

# Replicate Configuration
# Get your API token from: https://replicate.com/account/api-tokens
REPLICATE_API_TOKEN={replicate_token}

# Default API Usage (True for OpenAI, False for Ollama)
USE_OPENAI_API={use_openai}
"""
    
    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("\n✅ .env file created successfully!")
        print(f"📁 Location: {os.path.abspath('.env')}")
        
        if openai_key:
            print("🔑 OpenAI API key configured")
        else:
            print("⚠️  No OpenAI API key provided - will use Ollama only")
        
        print(f"🤖 Will use: {'OpenAI' if use_openai == 'True' else 'Ollama'}")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return
    
    print("\n🚀 Next steps:")
    print("1. Restart the backend: docker-compose restart backend")
    print("2. Test the application: http://localhost:5173")
    print("3. Check backend logs: docker-compose logs backend")

if __name__ == "__main__":
    try:
        create_env_file()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
