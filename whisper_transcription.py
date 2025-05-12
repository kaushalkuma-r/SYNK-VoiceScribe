import torch
from faster_whisper import WhisperModel

def initialize_whisper_model():
    """Initialize and return the Whisper model"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return WhisperModel("base", device=device)

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe an audio file using Whisper and return the transcription as a string.
    
    Args:
        audio_path (str): Path to the audio file to transcribe
        
    Returns:
        str: The transcribed text
    """
    # Initialize the model
    model = initialize_whisper_model()
    
    # Run the transcription with forced Hindi language
    segments, info = model.transcribe(audio_path, beam_size=5, language="hi")
    
    # Collect all segments into a single transcript
    transcript = ""
    for segment in segments:
        transcript += segment.text + " "
    
    return transcript.strip()

if __name__ == "__main__":
    # Example usage when run directly
    audio_file = "test.mp3"
    transcription = transcribe_audio(audio_file)
    print("Transcription:w", transcription)
