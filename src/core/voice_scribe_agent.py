import os
import logging
from typing import Annotated, TypedDict, Sequence
from pathlib import Path
from dotenv import load_dotenv
from faster_whisper import WhisperModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import torch
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AgentState(TypedDict):
    """State for the voice scribe agent."""
    audio_file_path: str
    raw_transcription: str | None
    sanitized_text: str | None
    error: str | None
    processing_time: float | None

class VoiceScribeAgent:
    def __init__(
        self,
        whisper_model: str = "base",
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        temperature: float = 0.7,
        compute_type: str = "float16" if torch.cuda.is_available() else "float32"
    ):
        """
        Initialize the Voice Scribe Agent.
        
        Args:
            whisper_model: Whisper model size ("tiny", "base", "small", "medium", "large")
            device: Device to run the model on ("cuda" or "cpu")
            temperature: Temperature for Gemini model
            compute_type: Compute type for faster-whisper ("float16", "float32", "int8")
        """
        logger.info(f"Initializing VoiceScribeAgent with {whisper_model} model on {device}")
        
        # Initialize Whisper model
        self.whisper_model = WhisperModel(
            whisper_model,
            device=device,
            compute_type=compute_type
        )
        
        # Initialize Gemini
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=temperature,
            google_api_key=os.environ["GOOGLE_API_KEY"]
        )
        
        # Initialize the sanitization chain
        self.sanitization_prompt =PromptTemplate(
            template=(
                "You are an expert transcript editor. "
                "Your tasks are to: "
                "1. Identify and translate any non-English text to English. "
                "2. Improve technical terminology while maintaining meaning. "
                "3. Enhance overall coherence. "
                "Here is the transcript: {transcript}"
            ),
            input_variables=["transcript"]
        )

        self.chain = self.sanitization_prompt | self.llm | StrOutputParser()
        
        # Create the graph
        self.workflow = self._create_workflow()
        
        logger.info("VoiceScribeAgent initialization complete")

    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow."""
        
        # Define the nodes
        def transcribe_audio(state: AgentState) -> AgentState:
            """Transcribe audio to text using faster-whisper."""
            try:
                import time
                start_time = time.time()
                
                audio_file_path = state["audio_file_path"]
                logger.info(f"Transcribing audio file: {audio_file_path}")
                
                # Transcribe using faster-whisper
                segments, info = self.whisper_model.transcribe(
                    audio_file_path,
                    beam_size=5
                )
                
                # Combine all segments
                text = " ".join([segment.text for segment in segments])
                
                processing_time = time.time() - start_time
                logger.info(f"Transcription completed in {processing_time:.2f} seconds")
                logger.info(f"Detected language: {info.language} (confidence: {info.language_probability:.2f})")
                
                return {
                    "raw_transcription": text,
                    "processing_time": processing_time
                }
            except Exception as e:
                logger.error(f"Transcription error: {str(e)}")
                return {"error": f"Transcription error: {str(e)}"}

        def sanitize_text(state: AgentState) -> AgentState:
            """Sanitize the transcribed text using Gemini."""
            try:
                if state.get("error"):
                    return state
                
                import time
                start_time = time.time()
                
                raw_text = state["raw_transcription"]
                logger.info("Starting text sanitization")
                
                sanitized_text = self.chain.invoke({"transcript": raw_text})
                
                processing_time = time.time() - start_time
                logger.info(f"Sanitization completed in {processing_time:.2f} seconds")
                
                return {
                    "sanitized_text": sanitized_text,
                    "processing_time": state.get("processing_time", 0) + processing_time
                }
            except Exception as e:
                logger.error(f"Sanitization error: {str(e)}")
                return {"error": f"Sanitization error: {str(e)}"}

        def should_continue(state: AgentState) -> str:
            """Determine if the workflow should continue."""
            if state.get("error"):
                return "end"
            return "continue"

        # Create the graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("transcribe", transcribe_audio)
        workflow.add_node("sanitize", sanitize_text)

        # Add edges
        workflow.add_edge("transcribe", "sanitize")
        workflow.add_conditional_edges(
            "sanitize",
            should_continue,
            {
                "continue": END,
                "end": END
            }
        )

        # Set entry point
        workflow.set_entry_point("transcribe")

        return workflow.compile()

    def process_audio(self, audio_file_path: str) -> dict:
        """
        Process an audio file through the workflow.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            dict: Contains raw_transcription, sanitized_text, processing_time, and error (if any)
        """
        logger.info(f"Starting audio processing for: {audio_file_path}")
        
        # Validate file exists
        if not os.path.exists(audio_file_path):
            error_msg = f"Audio file not found: {audio_file_path}"
            logger.error(error_msg)
            return {"error": error_msg}
        
        # Initialize the state
        initial_state = {
            "audio_file_path": audio_file_path,
            "raw_transcription": None,
            "sanitized_text": None,
            "error": None,
            "processing_time": None
        }
        
        # Run the workflow
        final_state = self.workflow.invoke(initial_state)
        
        result = {
            "raw_transcription": final_state.get("raw_transcription"),
            "sanitized_text": final_state.get("sanitized_text"),
            "processing_time": final_state.get("processing_time"),
            "error": final_state.get("error")
        }
        
        if result["error"]:
            logger.error(f"Processing failed: {result['error']}")
        else:
            logger.info("Processing completed successfully")
            
        return result

def main():
    """Example usage of the VoiceScribeAgent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Voice Scribe Agent")
    parser.add_argument("audio_file", help="Path to the audio file")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large"],
                      help="Whisper model size")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu",
                      help="Device to run the model on (cuda/cpu)")
    parser.add_argument("--compute-type", default="float16" if torch.cuda.is_available() else "float32",
                      choices=["float16", "float32", "int8"],
                      help="Compute type for faster-whisper")
    parser.add_argument("--temperature", type=float, default=0.7,
                      help="Temperature for Gemini model")
    
    args = parser.parse_args()
    
    try:
        agent = VoiceScribeAgent(
            whisper_model=args.model,
            device=args.device,
            compute_type=args.compute_type,
            temperature=args.temperature
        )
        
        result = agent.process_audio(args.audio_file)
        
        if result["error"]:
            print(f"Error: {result['error']}")
        else:
            print("\nRaw Transcription:")
            print(result["raw_transcription"])
            print("\nSanitized Text:")
            print(result["sanitized_text"])
            print(f"\nTotal Processing Time: {result['processing_time']:.2f} seconds")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 