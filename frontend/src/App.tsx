import { useState } from 'react';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import AudioPlayer from './components/AudioPlayer';
import './styles/App.css';

interface ProcessedData {
  audio_url: string;
  text: string;
}

function App() {
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [extractedText, setExtractedText] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileProcessed = (data: ProcessedData) => {
    setAudioUrl(data.audio_url);
    setExtractedText(data.text);
    setLoading(false);
    setError(null);
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
    setLoading(false);
  };

  return (
    <div className="app-container">
      <Header />

      <main className="main-content">
        <section className="upload-section">
          <FileUpload
            onStartProcessing={() => setLoading(true)}
            onFileProcessed={handleFileProcessed}
            onError={handleError}
          />

          {loading && (
            <div className="loading-indicator">
              <p>Processing your file...</p>
              <div className="spinner"></div>
            </div>
          )}

          {error && (
            <div className="error-message">
              <p>Error: {error}</p>
            </div>
          )}
        </section>

        {audioUrl && (
          <section className="audio-section">
            <h2>Audio Playback</h2>
            <AudioPlayer audioUrl={audioUrl} />

            <div className="text-preview">
              <h3>Extracted Text Preview</h3>
              <div className="text-content">{extractedText}</div>
            </div>
          </section>
        )}

        <section className="info-section">
          <h2>About AI Accessibility Reader</h2>
          <p>
            This tool helps visually impaired individuals access text content through speech.
            Simply upload a text file, and the AI will convert it to natural-sounding speech that you can play, pause, and control.
          </p>
          <p>
            The AI Accessibility Reader is aligned with <strong>Sustainable Development Goal 10</strong>:
            Reduced Inequalities, as it strives to bridge the accessibility gap and promote inclusivity.
          </p>
          <p>
            Unlike traditional online text-to-speech services, our tool functions offline,
            ensuring privacy, cost-effectiveness, and usability in areas with limited internet access.
          </p>
        </section>
      </main>

      <footer className="app-footer">
        <p>&copy; 2025 AI Accessibility Reader | Aligned with SDG 10: Reduced Inequalities</p>
      </footer>
    </div>
  );
}

export default App;
