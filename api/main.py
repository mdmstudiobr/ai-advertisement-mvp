from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from imageTools import enhance_image, remove_background, enhance_image_replicate
from aiGenerator import generate_ad
from fastapi.responses import StreamingResponse
from io import BytesIO

app = FastAPI()

# Allow frontend to access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CarInfo(BaseModel):
    make: str
    model: str
    year: str
    km: str
    fuel: str
    transmission: str
    prompt: str = None  # Optional custom prompt

@app.post("/generate-ad")
def generate_ad_route(info: CarInfo):
    # Use custom prompt if provided, otherwise use default English prompt
    if info.prompt:
        # For Spanish and Portuguese, use the custom prompt
        return generate_ad(
            info.make, info.model, info.year,
            info.km, info.fuel, info.transmission,
            custom_prompt=info.prompt
        )
    else:
        # Default English prompt - return aiGenerator response directly
        return generate_ad(
            info.make, info.model, info.year,
            info.km, info.fuel, info.transmission
        )

@app.post("/enhance-image")
async def enhance_image_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    result_bytes = enhance_image(contents)
    return StreamingResponse(BytesIO(result_bytes), media_type="image/jpeg")



@app.post("/enhance-image-replicate")
async def enhance_image_replicate_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        result_bytes = enhance_image_replicate(contents)
        if result_bytes is None:
            return {"error": "Replicate AI generation failed. Please check your API key and credits."}
        return StreamingResponse(BytesIO(result_bytes), media_type="image/png")
    except Exception as e:
        return {"error": f"Error processing image: {str(e)}"}

@app.post("/remove-bg")
async def remove_bg_route(file: UploadFile = File(...)):
    img_bytes = await file.read()
    removed = remove_background(img_bytes)
    return {"image": removed.hex()}