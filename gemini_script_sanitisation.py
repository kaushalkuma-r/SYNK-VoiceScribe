import os
from typing import TypedDict
from whisper_transcription import transcribe_audio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import LLMChain
from langgraph.graph import StateGraph, END
import re
from difflib import SequenceMatcher

# Define the state for the graph
class TranscriptState(TypedDict):
    transcript: str
    sanitized: bool
    error: str | None

# Sanitisation node using Gemini LLM

def sanitise_transcript_node(state: TranscriptState) -> TranscriptState:
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.environ["GOOGLE_API_KEY"]
        )
        prompt = PromptTemplate(
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
        chain = LLMChain(llm=llm, prompt=prompt, output_parser=StrOutputParser())
        result = chain.invoke({"transcript": state["transcript"]})
        return TranscriptState(
            transcript=result,
            sanitized=True,
            error=None
        )
    except Exception as e:
        return TranscriptState(
            transcript=state["transcript"],
            sanitized=False,
            error=str(e)
        )

def process_audio_transcript(audio_path: str) -> str:
    # Get initial transcript from Whisper
    raw_transcript = transcribe_audio(audio_path)
    # Build the graph
    workflow = StateGraph(TranscriptState)
    workflow.add_node("sanitise", sanitise_transcript_node)
    workflow.set_entry_point("sanitise")
    workflow.add_edge("sanitise", END)
    app = workflow.compile()
    # Run the workflow
    initial_state = TranscriptState(
        transcript=raw_transcript,
        sanitized=False,
        error=None
    )
    final_state = app.invoke(initial_state)
    if final_state["error"]:
        print(f"Warning: {final_state['error']}")
        return raw_transcript
    return final_state["transcript"]

def analyze_transcripts(original: str, new: str) -> dict:
    """
    Analyze the original and new transcripts using relevant metrics.
    Metrics include:
    - Word count
    - Sentence count
    - Similarity score (using difflib.SequenceMatcher)
    """
    def count_words(text: str) -> int:
        return len(re.findall(r'\b\w+\b', text))

    def count_sentences(text: str) -> int:
        return len(re.findall(r'[.!?]+', text))

    def similarity_score(a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

    original_words = count_words(original)
    new_words = count_words(new)
    original_sentences = count_sentences(original)
    new_sentences = count_sentences(new)
    similarity = similarity_score(original, new)

    return {
        "original_word_count": original_words,
        "new_word_count": new_words,
        "original_sentence_count": original_sentences,
        "new_sentence_count": new_sentences,
        "similarity_score": similarity
    }

if __name__ == "__main__":
    audio_file = "test.mp3"
    original_transcript = transcribe_audio(audio_file)
    final_transcript = process_audio_transcript(audio_file)
    print("Original Transcript:", original_transcript)
    print("Final Processed Transcript:", final_transcript)
    analysis = analyze_transcripts(original_transcript, final_transcript)
    print("Analysis:", analysis)


