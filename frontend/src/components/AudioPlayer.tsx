import { useState, useRef, useEffect } from 'react';
import '../styles/AudioPlayer.css';

interface AudioPlayerProps {
  audioUrl: string;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({ audioUrl }) => {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
      setCurrentTime(0);
      setLoading(true);

      const fullUrl = audioUrl.startsWith('http')
        ? audioUrl
        : `http://localhost:5000${audioUrl}`;

      audioRef.current.src = fullUrl;
      audioRef.current.load();
    }
  }, [audioUrl]);

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
      setLoading(false);
    }
  };

  const togglePlayPause = () => {
    if (!audioRef.current) return;

    if (audioRef.current.paused) {
      audioRef.current.play();
      setIsPlaying(true);
    } else {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  const handleStop = () => {
    if (!audioRef.current) return;
    audioRef.current.pause();
    audioRef.current.currentTime = 0;
    setIsPlaying(false);
    setCurrentTime(0);
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!audioRef.current) return;
    const seekTime = (parseFloat(e.target.value) / 100) * duration;
    audioRef.current.currentTime = seekTime;
    setCurrentTime(seekTime);
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  const progressPercentage = duration ? (currentTime / duration) * 100 : 0;

  return (
    <div className="audio-player">
      <audio
        ref={audioRef}
        onLoadedMetadata={handleLoadedMetadata}
        onTimeUpdate={handleTimeUpdate}
        onEnded={() => setIsPlaying(false)}
      />

      {loading ? (
        <div className="loading-audio">
          <div className="loading-spinner"></div>
          <p>Loading audio...</p>
        </div>
      ) : (
        <>
          <div className="player-controls">
            <button
              className={`control-button ${isPlaying ? 'pause' : 'play'}`}
              onClick={togglePlayPause}
              aria-label={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? (
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="6" y="4" width="4" height="16" />
                  <rect x="14" y="4" width="4" height="16" />
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polygon points="5 3 19 12 5 21 5 3" />
                </svg>
              )}
            </button>

            <button
              className="control-button stop"
              onClick={handleStop}
              aria-label="Stop"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="6" y="6" width="12" height="12" />
              </svg>
            </button>
          </div>

          <div className="progress-container">
            <span className="time-display">{formatTime(currentTime)}</span>
            <input
              type="range"
              className="progress-bar"
              value={progressPercentage}
              onChange={handleSeek}
              min="0"
              max="100"
              step="0.1"
              aria-label="Audio progress"
            />
            <span className="time-display">{formatTime(duration)}</span>
          </div>

          <div className="audio-info">
            <p className="audio-title">Generated Audio</p>
            <a
              href={`http://localhost:5000${audioUrl}`}
              download
              className="download-link"
              aria-label="Download audio file"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Download
            </a>
          </div>
        </>
      )}
    </div>
  );
};

export default AudioPlayer;
