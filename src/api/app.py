from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from src.core.voice_scribe_agent import VoiceScribeAgent
import os
import tempfile
from pathlib import Path
import logging
from typing import Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Scribe API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/static/frontend"), name="static")

# Initialize the agent
agent = VoiceScribeAgent(
    whisper_model="base",
    device="cuda" if os.environ.get("USE_GPU", "false").lower() == "true" else "cpu"
)

@app.get("/")
async def read_root():
    return FileResponse("src/static/frontend/index.html")

@app.post("/transcribe")
async def transcribe_audio(request: Request, file: UploadFile = File(...)):
    try:
        logger.info(f"Received file: {file.filename}")
        logger.info(f"Content type: {file.content_type}")
        
        # Validate file type
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Create a temporary file to store the uploaded audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
            logger.info(f"Saved file to: {temp_file_path}")

        # Process the audio file
        logger.info("Starting audio processing")
        result = agent.process_audio(temp_file_path)
        logger.info("Audio processing complete")

        # Clean up the temporary file
        os.unlink(temp_file_path)
        logger.info("Temporary file cleaned up")

        if result.get("error"):
            logger.error(f"Processing error: {result['error']}")
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