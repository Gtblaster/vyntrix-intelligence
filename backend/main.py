from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from model import predict_image, predict_text

app = FastAPI(title="Vyntrix Intelligence AI Engine")

# Add CORS middleware to allow the frontend to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production this should be restricted to the frontend origin (e.g., "http://127.0.0.1:8000")
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "model": "Vyntrix Deep Learning Engine V1.0"}

@app.post("/scan-image/")
async def scan_image(file: UploadFile = File(...)):
    """
    Receives an uploaded image, processes it through the PyTorch model, and returns the prediction.
    """
    # Quick check for supported file types
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    # Read the file bytes
    image_bytes = await file.read()
    
    # Run prediction using the model
    prediction_result = predict_image(image_bytes)
    
    if not prediction_result.get("success"):
        raise HTTPException(status_code=500, detail=f"Model Inference Error: {prediction_result.get('error')}")
        
    return prediction_result

from pydantic import BaseModel

class TextInput(BaseModel):
    text: str

@app.post("/scan-text/")
async def scan_text(payload: TextInput):
    """
    Receives raw text or a URL, processes it through the NLP model, and returns the prediction.
    """
    if len(payload.text) > 5000:
         raise HTTPException(status_code=400, detail="Text payload too large. Max 5000 characters.")
         
    # Run prediction using the NLP model
    prediction_result = predict_text(payload.text)
    
    if not prediction_result.get("success"):
        raise HTTPException(status_code=500, detail=f"NLP Inference Error: {prediction_result.get('error')}")
        
    return prediction_result
