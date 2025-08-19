import cv2
import numpy as np
from rembg import remove
from PIL import Image
import io
import base64
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
import replicate

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Replicate client
replicate_client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

def enhance_image(input_bytes):
    np_arr = np.frombuffer(input_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Brightness & contrast
    alpha = 1.3
    beta = 30
    bright = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    # Sharpen
    kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
    sharpened = cv2.filter2D(bright, -1, kernel)

    # Encode as JPEG
    _, buf = cv2.imencode(".jpg", sharpened)
    return buf.tobytes()

def enhance_image_replicate(input_bytes):
    """
    Enhance vehicle image using Replicate's realistic-vision-v5.1 model.
    Returns None if Replicate fails - no fallback to Python enhancement.
    """

    try:
        api_token = os.getenv("REPLICATE_API_TOKEN")
        print(f"🔑 API Token check: {'Present' if api_token else 'Missing'} (Length: {len(api_token) if api_token else 0})")
        
        if not api_token or "your_replicate_api_token_here" in api_token:
            print("⚠️ Replicate token not found or invalid")
            return None

        # Open image and validate
        if len(input_bytes) < 100:
            raise ValueError("Invalid image data: too small")

        try:
            image = Image.open(io.BytesIO(input_bytes))
            print(f"🔍 Image loaded: {image.format}, {image.size}, {image.mode}")
        except Exception as err:
            raise ValueError(f"Failed to open image: {err}")

        if image.mode != 'RGB':
            image = image.convert('RGB')
            print("🎨 Converted to RGB")

        # Save as PNG
        png_buffer = io.BytesIO()
        image.save(png_buffer, format='PNG')
        png_buffer.seek(0)
        png_bytes = png_buffer.getvalue()

        if not png_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError("Invalid PNG header")

        print(f"✅ PNG valid, sending {len(png_bytes)} bytes to Replicate")

        # Enhanced prompt for better AI generation
        prompt = (
            "Transform this vehicle photo into a stunning, professional automotive advertisement image. "
            "Enhance the vehicle to look brand new, polished, and showroom-ready. "
            "Create a clean, modern background with perfect lighting - like a professional car photography studio. "
            "Maintain the exact vehicle shape, color, and perspective while dramatically improving quality. "
            "Add subtle reflections, enhance details, and create a premium aesthetic suitable for luxury car sales."
        )

        negative_prompt = "people, logos, text, watermark, blurry, low quality, cropped, distorted, old, dirty, damaged, background clutter"

        print("🚀 Calling Replicate (stable-diffusion-v1-5)...")

        # Run AI inference with a more reliable model
        output = replicate.run(
            "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
            input={
                "image": png_buffer,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_inference_steps": 20,
                "guidance_scale": 7.5,
                "strength": 0.7,
                "scheduler": "K_EULER"
            }
        )

        if not output:
            raise RuntimeError("No output received from Replicate")
        
        # Handle different output formats from Replicate
        if isinstance(output, list) and len(output) > 0:
            image_url = output[0]
        elif hasattr(output, 'url'):
            image_url = output.url
        elif hasattr(output, '__str__'):
            image_url = str(output)
        else:
            raise RuntimeError(f"Unexpected output format from Replicate: {type(output)}")
        
        if not str(image_url).startswith("http"):
            raise RuntimeError(f"Invalid image URL from Replicate: {image_url}")

        print(f"✅ AI generated image ready: {image_url}")
        response = requests.get(image_url)
        response.raise_for_status()
        return response.content

    except Exception as err:
        print(f"❌ Replicate AI generation failed: {err}")
        # Return None to indicate failure - no fallback
        return None

def remove_background(input_bytes):
    input_image = Image.open(io.BytesIO(input_bytes))
    output_image = remove(input_image)
    output_buffer = io.BytesIO()
    output_image.save(output_buffer, format="PNG")
    return output_buffer.getvalue()