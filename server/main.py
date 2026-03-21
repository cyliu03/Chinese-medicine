import os
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from predictor import TCMFormulaPredictor
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TCM Formula Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.getenv("MODEL_PATH", "../training/checkpoints/best_model.pt")
VOCAB_DIR = os.getenv("VOCAB_DIR", "../data/chatmed")

model = None

@app.on_event("startup")
async def startup_event():
    global model
    if not os.path.exists(MODEL_PATH):
        print(f"Warning: Model not found at {MODEL_PATH}")
    else:
        model = TCMFormulaPredictor(MODEL_PATH, VOCAB_DIR)

class PredictionRequest(BaseModel):
    symptoms: List[str]

class PredictionResponse(BaseModel):
    status: str
    herbs: List[dict] = []
    valid_symptoms: List[str] = []
    message: str = ""

@app.get("/")
async def root():
    return {"message": "TCM Formula API is running", "model_loaded": model is not None}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        result = model.predict(request.symptoms)
        return PredictionResponse(
            status="success",
            herbs=result["herbs"],
            valid_symptoms=result["valid_symptoms"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
