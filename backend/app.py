import os
import uuid
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import text_processor
import tts_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'static/audio'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER

# Create necessary directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return 'Backend API is alive and kicking!'

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify TTS engine status"""
    try:
        # Try to initialize TTS engine if not already done
        if tts_engine.current_tts_engine is None:
            tts_engine.initialize_tts()
        
        engine_info = tts_engine.get_current_engine()
        available_engines = tts_engine.get_available_engines()
        
        return jsonify({
            'status': 'healthy',
            'tts_ready': True,
            'message': 'TTS engine is ready',
            'current_engine': engine_info,
            'available_engines': available_engines
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        available_engines = tts_engine.get_available_engines()
        return jsonify({
            'status': 'unhealthy',
            'tts_ready': False,
            'error': str(e),
            'message': 'TTS engine failed to initialize',
            'available_engines': available_engines
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload, extract text, and convert to speech"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Please upload .txt, .pdf, or .docx files.'}), 400

    try:
        # Generate secure filename with UUID to avoid collisions
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        
        # Save uploaded file
        file.save(file_path)
        logger.info(f"File saved: {file_path}")
        
        # Extract text from file
        logger.info("Extracting text from file...")
        text = text_processor.extract_text(file_path)
        
        if not text or not text.strip():
            return jsonify({'error': 'No text could be extracted from the file'}), 400
        
        logger.info(f"Extracted {len(text)} characters of text")
        
        # Convert text to speech
        audio_filename = f"{file_id}.wav"  # Changed to WAV since MP3 might not work without ffmpeg
        audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)
        
        logger.info("Converting text to speech...")
        tts_engine.text_to_speech(text, audio_path)
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except Exception as cleanup_error:
            logger.warning(f"Failed to clean up uploaded file: {cleanup_error}")
        
        return jsonify({
            'success': True,
            'message': 'File processed successfully',
            'audio_url': f"/api/audio/{audio_filename}",
            'text': text[:1000] + ('...' if len(text) > 1000 else ''),  # Return preview of text
            'text_length': len(text),
            'audio_file': audio_filename
        }), 200
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return jsonify({'error': f'File processing error: {str(ve)}'}), 400
        
    except RuntimeError as re:
        logger.error(f"Runtime error: {str(re)}")
        return jsonify({'error': f'TTS engine error: {str(re)}'}), 500
        
    except Exception as e:
        logger.exception("Unexpected error during file processing")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/api/audio/<filename>', methods=['GET'])
def get_audio(filename):
    """Serve the generated audio file"""
    # Validate filename to prevent directory traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    audio_path = os.path.join(app.config['AUDIO_FOLDER'], filename)
    
    if os.path.exists(audio_path):
        try:
            # Determine MIME type based on file extension
            if audio_path.endswith('.wav'):
                mimetype = 'audio/wav'
            else:
                mimetype = 'audio/mpeg'
            return send_file(audio_path, mimetype=mimetype)
        except Exception as e:
            logger.error(f"Error serving audio file {filename}: {str(e)}")
            return jsonify({'error': 'Error serving audio file'}), 500
    else:
        logger.warning(f"Audio file not found: {audio_path}")
        return jsonify({'error': 'Audio file not found'}), 404

@app.route('/api/models', methods=['GET'])
def get_available_models():
    """Get list of available TTS engines for debugging"""
    try:
        available_engines = tts_engine.get_available_engines()
        current_engine = tts_engine.get_current_engine()
        
        return jsonify({
            'available_engines': available_engines,
            'current_engine': current_engine
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Please upload a smaller file.'}), 413

@app.errorhandler(500)
def internal_error(e):
    logger.exception("Internal server error")
    return jsonify({'error': 'Internal server error. Please try again later.'}), 500

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    
    # Show available engines
    available_engines = tts_engine.get_available_engines()
    logger.info(f"Available TTS engines: {available_engines}")
    
    # Pre-initialize TTS engine to catch errors early
    try:
        logger.info("Pre-initializing TTS engine...")
        tts_engine.initialize_tts()
        current_engine = tts_engine.get_current_engine()
        logger.info(f"TTS engine pre-initialization successful: {current_engine}")
    except Exception as e:
        logger.error(f"TTS engine pre-initialization failed: {str(e)}")
        logger.info("Application will start anyway, but TTS functionality may be limited")
    
    app.run(debug=True, port=5000)