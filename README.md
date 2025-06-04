# SYNK Voice Scribe

A powerful voice-to-text transcription application that converts spoken words into written text in real-time, featuring AI-powered text sanitization.

## Features

- Real-time voice-to-text transcription using Whisper
- AI-powered text sanitization using Gemini
- Modern, responsive web interface
- Support for multiple audio formats
- High accuracy speech recognition
- Cross-platform compatibility
- Processing time tracking
- Error handling and logging

## Project Structure

```
SYNK-Voice-Scribe/
├── src/
│   ├── api/            # FastAPI application and routes
│   ├── core/           # Core business logic
│   ├── utils/          # Utility functions
│   └── static/         # Static files
│       └── frontend/   # Frontend assets
├── tests/              # Test files
├── docs/              # Documentation
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

## Prerequisites

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

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
   - Create a `.env` file in the root directory
   - Add your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   USE_GPU=true  # Set to false if you don't have a GPU
   ```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

2. Open your browser and go to `http://localhost:8000`

## API Endpoints

- `POST /transcribe`: Upload and process an audio file
  - Accepts: audio file (multipart/form-data)
  - Returns: JSON with raw transcription, sanitized text, and processing time

- `GET /health`: Health check endpoint
  - Returns: API status

## Development

### Backend Structure
- `src/api/app.py`: FastAPI application and endpoints
- `src/core/voice_scribe_agent.py`: Core transcription and sanitization logic
- `src/utils/`: Utility functions and helpers

### Frontend Structure
- `src/static/frontend/index.html`: Main HTML file with embedded JavaScript
- `src/static/frontend/styles.css`: Custom styles (if needed)

## Testing

Run the test suite:
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

- Kaushal Kumar
- GitHub: [@kaushalkuma-r](https://github.com/kaushalkuma-r)

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to the open-source community for their invaluable resources and tools