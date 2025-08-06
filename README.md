# Medical Receptionist AI Chatbot

An AI-powered medical receptionist system that handles patient verification calls through both text and voice interactions. Built with Flask, ElevenLabs TTS, and Groq AI.

## Features

- **Voice-to-Voice Interaction**: Full conversational AI with speech recognition and text-to-speech
- **Patient Verification**: Automated verification against patient database using name, phone, and date of birth
- **Multiple Voice Options**: 8 different AI voices (male/female, various tones)
- **Session Management**: Maintains conversation context across interactions
- **Real-time Audio**: Instant speech synthesis and playback
- **RESTful API**: Clean endpoints for integration with other systems

## Technology Stack

- **Backend**: Flask (Python)
- **AI Model**: Groq LLaMA 3 8B
- **Text-to-Speech**: ElevenLabs API
- **Speech Recognition**: Google Speech Recognition
- **Frontend**: HTML/JavaScript (template-based)

## Available Voices

- **Aria**: Female, Professional
- **Rachel**: Female, Calm
- **Adam**: Male, Professional
- **Josh**: Male, Friendly
- **Arnold**: Male, Deep
- **Bella**: Female, Warm
- **Elli**: Female, Young
- **James**: Male, Mature

## Installation

### Prerequisites

- Python 3.8+
- Microphone access for voice input
- Internet connection for API calls

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd medical-receptionist-ai
   ```

2. **Install dependencies**
   ```bash
   pip install flask flask-cors requests python-dotenv elevenlabs speechrecognition pyaudio
   ```

3. **Create environment file**
   ```bash
   touch .env
   ```

4. **Add API keys to `.env`**
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ```

5. **Create patient data file**
   Create `data.json` in the project root:
   ```json
   {
     "patients": [
       {
         "name": "John Smith",
         "phone": "555-0123",
         "date_of_birth": "1985-06-15",
         "appointment_date": "2024-02-15",
         "appointment_time": "10:30 AM"
       }
     ]
   }
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

## API Endpoints

### Chat Endpoints
- `POST /chat` - Text-based conversation
- `POST /voice_chat` - Voice-to-voice interaction
- `POST /speak` - Generate speech from text
- `GET /get_audio` - Retrieve generated audio file

### Utility Endpoints
- `GET /` - Web interface
- `GET /voices` - List available voices
- `GET /status` - System health check
- `POST /reset` - Clear conversation history

### Request/Response Examples

**Text Chat:**
```json
POST /chat
{
  "message": "Hi, I'd like to verify my appointment",
  "session_id": "user123",
  "voice_id": "pFZP5JQG7iQjIQuC4Bku"
}

Response:
{
  "response": "Hello! I can help verify your appointment. Could you please tell me your full name?",
  "session_id": "user123",
  "message_count": 2,
  "speech_enabled": true,
  "audio_available": true
}
```

**Voice Chat:**
```json
POST /voice_chat
{
  "session_id": "user123",
  "voice_id": "21m00Tcm4TlvDq8ikWAM"
}

Response:
{
  "user_input": "My name is John Smith",
  "response": "Thank you, John. Now could you please provide your phone number?",
  "session_id": "user123",
  "message_count": 4,
  "speech_enabled": true,
  "audio_available": true
}
```

## Usage

### Web Interface
1. Open browser to `http://localhost:5000`
2. Choose between text or voice interaction
3. Select preferred AI voice
4. Follow the verification prompts

### Voice Interaction Flow
1. System greets caller
2. Requests patient name
3. Requests phone number
4. Requests date of birth
5. Verifies against database
6. Confirms appointment or indicates no match

## Configuration

### Environment Variables
- `GROQ_API_KEY`: Required for AI responses
- `ELEVENLABS_API_KEY`: Required for text-to-speech

### Patient Data Structure
The system expects a JSON file with patient records containing:
- `name`: Full patient name
- `phone`: Phone number (flexible formatting)
- `date_of_birth`: YYYY-MM-DD format
- `appointment_date`: Appointment date
- `appointment_time`: Appointment time

## Error Handling

The system includes comprehensive error handling for:
- Missing API keys
- Network connectivity issues
- Speech recognition failures
- Audio generation problems
- Invalid patient data
- Session management errors

## Security Considerations

- API keys are loaded from environment variables
- No sensitive patient data is logged
- Session data is stored in memory (not persistent)
- CORS is enabled for web interface integration

## Troubleshooting

### Common Issues

1. **"No module named 'pyaudio'"**
   ```bash
   # On Windows
   pip install pyaudio
   
   # On macOS
   brew install portaudio
   pip install pyaudio
   
   # On Linux
   sudo apt-get install python3-pyaudio
   ```

2. **Microphone not working**
   - Check microphone permissions
   - Verify microphone is not used by other applications
   - Test with `speech_recognition` library directly

3. **API key errors**
   - Verify keys are correctly set in `.env` file
   - Check API key permissions and quotas
   - Ensure environment file is in the correct location

4. **Audio playback issues**
   - Check system audio settings
   - Verify browser audio permissions
   - Test with different audio formats

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation for Groq and ElevenLabs
3. Create an issue in the repository

