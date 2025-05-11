# SYNK-VoiceScribe

SYNK-VoiceScribe is a powerful voice-to-text transcription application that converts spoken words into written text in real-time. This application features a modern web interface for easy audio file upload and transcription processing.

## Features

- Real-time voice-to-text transcription using Whisper
- AI-powered text sanitization using Gemini
- Modern, responsive web interface
- Support for multiple audio formats
- High accuracy speech recognition
- Cross-platform compatibility
- Processing time tracking
- Error handling and logging

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- A working microphone
- Google API key for Gemini
- Node.js and npm (for frontend development)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kaushalkuma-r/SYNK-VoiceScribe.git
cd SYNK-VoiceScribe
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
   - Create a `.env` file in the root directory
   - Add your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   USE_GPU=true  # Set to false if you don't have a GPU
   ```

## Running the Application

### Backend (FastAPI)

1. Start the FastAPI server:
```bash
uvicorn app:app --reload
```
The API will be available at `http://localhost:8000`

### Frontend

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Start a local server (using Python's built-in server):
```bash
python -m http.server 3000
```

3. Open your browser and go to `http://localhost:3000`

## Usage

1. Open the web interface in your browser
2. Click the upload area or drag and drop an audio file
3. Click "Transcribe" to process the audio
4. View the raw transcription and sanitized text
5. The processing time will be displayed at the bottom

## API Endpoints

- `POST /transcribe`: Upload and process an audio file
  - Accepts: audio file (multipart/form-data)
  - Returns: JSON with raw transcription, sanitized text, and processing time

- `GET /health`: Health check endpoint
  - Returns: API status

## Development

### Backend Structure
- `app.py`: FastAPI application and endpoints
- `voice_scribe_agent.py`: Core transcription and sanitization logic

### Frontend Structure
- `frontend/index.html`: Main HTML file
- `frontend/app.js`: React application code

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

- Kaushal Kumar
- GitHub: [@kaushalkuma-r](https://github.com/kaushalkuma-r)

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to the open-source community for their invaluable resources and tools