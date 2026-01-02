# AI Accessibility Reader

The AI Accessibility Reader is a web-based tool designed to enhance digital accessibility for visually impaired individuals by converting text files into speech. This project aligns with **Sustainable Development Goal 10: Reduced Inequalities**, promoting inclusivity in digital content access.

## Features

- Text-to-speech conversion for various file formats (TXT, PDF, DOCX)
- User-friendly interface with drag-and-drop file upload
- Interactive audio playback controls (Play, Pause, Stop)
- Text preview of uploaded content
- Offline speech synthesis using Coqui TTS
- Downloadable audio files

## Project Structure

The project is built with:
- **Frontend**: React/Vite
- **Backend**: Python/Flask
- **Text-to-Speech Engine**: Coqui TTS

## Installation and Setup

### Prerequisites

- Node.js (v16 or later)
- Python (v3.8 or later)
- FFmpeg (for audio processing)

### Backend Setup

1. Create a Virtual Environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Start the Flask server:
   ```bash
   python app.py
   ```
   The server will run on http://localhost:5000

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```
   The application will be available at http://localhost:3000

## Usage

1. Open the application in your browser
2. Upload a text file (TXT, PDF, or DOCX)
3. Wait for the text-to-speech conversion to complete
4. Use the audio player controls to listen to the content
5. Optionally download the audio file for later use

## Project Alignment with SDG 10

This project addresses a critical aspect of inequality by making digital content more accessible to visually impaired individuals. By providing a free, user-friendly text-to-speech tool that works offline, it ensures visually impaired users can independently access and understand written information without relying on costly software.

## Future Improvements

- Support for more file formats
- Multiple language support
- Voice customization options (pitch, speed, gender)
- Enhanced text extraction for complex documents
- Mobile application version

## License

This project is open-source and available under the MIT License.
