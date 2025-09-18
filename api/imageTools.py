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
    Enhance vehicle photo using Replicate's realistic-vision-v5.1 model (img2img mode).
    Preserves original car while enhancing background, lighting, clarity and removing distractions.
    """

    try:
        api_token = os.getenv("REPLICATE_API_TOKEN")
        if not api_token:
            raise ValueError("Replicate API token is missing or invalid.")
        
        if len(input_bytes) < 100:
            raise ValueError("Invalid image: too small.")

        # Open and convert image
        image = Image.open(io.BytesIO(input_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        print(f"✅ Image loaded: {image.size}, format: {image.format}")
        
        # Save reference image as base64 for future use
        reference_base64 = image_to_base64(input_bytes)
        if reference_base64:
            print(f"📸 Reference image saved as base64 for future use")

        # Save to PNG buffer
        png_buffer = io.BytesIO()
        image.save(png_buffer, format='PNG')
        png_buffer.seek(0)
        png_bytes = png_buffer.getvalue()

        if not png_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError("Not a valid PNG")

        print(f"📤 Sending image ({len(png_bytes)} bytes) to Replicate...")

        # Optimized prompt for EXACT vehicle preservation with color change
        prompt = (
            "Realistic photo enhancement of the given image. "
            "Preserve EXACTLY the same vehicle: same shape, model, brand, proportions, camera angle - EVERYTHING identical. "
            "ONLY change: transform the vehicle color to a beautiful metallic light blue color while keeping the exact same finish and reflections. "
            "Enhance: lighting, sharpness, shadows, paint shine, reflections, and background cleanliness. "
            "Keep the same background composition and location, but remove floor stains, trash, and distracting objects behind. "
            "The result must look like the exact same vehicle in the exact same photo, but now painted in a stunning metallic light blue color."
        )

        negative_prompt = (
            "fantasy, different car, changed shape, modified model, wrong color, distortion, broken proportions, artistic, painting, cartoon, illustration, anime, surreal, futuristic, concept car, deformed wheels, extra logos, people, text, watermark"
        )

        # Call the correct model with specific version - VERY CONSERVATIVE settings
        output = replicate.run(
            "lucataco/realistic-vision-v5-img2img:82bbb4595458d6be142450fc6d8c4d79c936b92bd184dd2d6dd71d0796159819",
            input={
                "image": png_buffer,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_inference_steps": 30,
                "guidance_scale": 3.5,
                "strength": 0.15,
                "seed": 123  # fixo para testes consistentes
            }
        )

        # Parse output according to Replicate documentation
        if hasattr(output, 'url') and callable(output.url):
            image_url = output.url()
            print(f"🖼️ Enhanced image URL: {image_url}")
        elif hasattr(output, 'url') and isinstance(output.url, str):
            image_url = output.url
            print(f"🖼️ Enhanced image URL: {image_url}")
        elif isinstance(output, list) and output:
            image_url = output[0]
            print(f"🖼️ Enhanced image URL: {image_url}")
        elif isinstance(output, str):
            image_url = output
            print(f"🖼️ Enhanced image URL: {image_url}")
        else:
            print(f"🔍 Debug - Output type: {type(output)}, value: {output}")
            raise RuntimeError(f"Unexpected output format from Replicate: {type(output)}")

        # Download result
        result = requests.get(image_url)
        result.raise_for_status()
        return result.content

    except Exception as err:
        print(f"❌ Replicate enhancement failed: {err}")
        return None

def realistic_vision_v5(input_bytes):
    """
    Enhance vehicle photo using Replicate's realistic-vision-v5.1 model (img2img mode).
    Preserves original car while enhancing background, lighting, clarity and removing distractions.
    """

    try:
        api_token = os.getenv("REPLICATE_API_TOKEN")
        if not api_token:
            raise ValueError("Replicate API token is missing or invalid.")
        
        if len(input_bytes) < 100:
            raise ValueError("Invalid image: too small.")

        # Open and convert image
        image = Image.open(io.BytesIO(input_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        print(f"✅ Image loaded: {image.size}, format: {image.format}")
        
        # Save reference image as base64 for future use
        reference_base64 = image_to_base64(input_bytes)
        if reference_base64:
            print(f"📸 Reference image saved as base64 for future use")

        # Save to PNG buffer
        png_buffer = io.BytesIO()
        image.save(png_buffer, format='PNG')
        png_buffer.seek(0)
        png_bytes = png_buffer.getvalue()

        if not png_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError("Not a valid PNG")

        print(f"📤 Sending image ({len(png_bytes)} bytes) to Replicate...")

        # Optimized prompt for EXACT car preservation
        prompt = (
            "Professional car photo enhancement. Keep EXACTLY the same car: identical color, size, shape, angle, model, brand, proportions, position. "
            "Only improve: lighting quality, paint shine, background cleanliness, remove dirt/stains, enhance reflections. "
            "Maintain 100% original car appearance and perspective."
        )

        negative_prompt = (
            "different car, different model, different color, different size, different shape, different angle, "
            "cartoon, painting, illustration, anime, artistic style, people, logos, watermark, text, "
            "distortion, surreal, unrealistic, modified car, altered proportions"
        )

        # Call the correct model with specific version - VERY CONSERVATIVE settings
        output = replicate.run(
            "lucataco/realistic-vision-v5-img2img:82bbb4595458d6be142450fc6d8c4d79c936b92bd184dd2d6dd71d0796159819",
            input={
                "image": png_buffer,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_inference_steps": 35,        # Menos passos = menos mudanças
                "guidance_scale": 5,            # Muito baixo = menos "criatividade"
                "strength": 0.2                  # EXTREMAMENTE baixo = quase não muda a imagem
            }
        )

        # Parse output according to Replicate documentation
        if hasattr(output, 'url') and callable(output.url):
            image_url = output.url()
            print(f"🖼️ Enhanced image URL: {image_url}")
        elif hasattr(output, 'url') and isinstance(output.url, str):
            image_url = output.url
            print(f"🖼️ Enhanced image URL: {image_url}")
        elif isinstance(output, list) and output:
            image_url = output[0]
            print(f"🖼️ Enhanced image URL: {image_url}")
        elif isinstance(output, str):
            image_url = output
            print(f"🖼️ Enhanced image URL: {image_url}")
        else:
            print(f"🔍 Debug - Output type: {type(output)}, value: {output}")
            raise RuntimeError(f"Unexpected output format from Replicate: {type(output)}")

        # Download result
        result = requests.get(image_url)
        result.raise_for_status()
        return result.content

    except Exception as err:
        print(f"❌ Replicate enhancement failed: {err}")
        return None

def remove_background(input_bytes):
    input_image = Image.open(io.BytesIO(input_bytes))
    output_image = remove(input_image)
    output_buffer = io.BytesIO()
    output_image.save(output_buffer, format="PNG")
    return output_buffer.getvalue()

def image_to_base64(image_bytes):
    """
    Convert image bytes to base64 string for storage and future use.
    """
    try:
        # Convert to base64
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        
        # Save to file for future reference
        with open('/tmp/reference_image_base64.txt', 'w') as f:
            f.write(base64_string)
        
        print(f"✅ Image converted to base64 and saved. Length: {len(base64_string)} characters")
        return base64_string
    except Exception as e:
        print(f"❌ Error converting to base64: {e}")
        return None

def base64_to_image(base64_string):
    """
    Convert base64 string back to image bytes.
    """
    try:
        image_bytes = base64.b64decode(base64_string)
        return image_bytes
    except Exception as e:
        print(f"❌ Error converting base64 to image: {e}")
        return None