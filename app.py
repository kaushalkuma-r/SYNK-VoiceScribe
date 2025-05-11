from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from voice_scribe_agent import VoiceScribeAgent
import os
import tempfile
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Scribe API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
agent = VoiceScribeAgent(
    whisper_model="base",
    device="cuda" if os.environ.get("USE_GPU", "false").lower() == "true" else "cpu"
)

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Create a temporary file to store the uploaded audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Process the audio file
        result = agent.process_audio(temp_file_path)

        # Clean up the temporary file
        os.unlink(temp_file_path)

        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])

        return JSONResponse(content={
            "raw_transcription": result["raw_transcription"],
            "sanitized_text": result["sanitized_text"],
            "processing_time": result["processing_time"]
        })

    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 