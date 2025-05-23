import { useState, useRef, ChangeEvent, DragEvent, MouseEvent, FormEvent } from 'react';
import axios from 'axios';
import '../styles/FileUpload.css';

interface FileUploadProps {
  onStartProcessing: () => void;
  onFileProcessed: (data: any) => void;
  onError: (message: string) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onStartProcessing, onFileProcessed, onError }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const allowedFileTypes = ['.txt', '.pdf', '.docx'];

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      validateAndSetFile(file);
    }
  };

  const validateAndSetFile = (file: File) => {
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (allowedFileTypes.includes(fileExtension)) {
      setSelectedFile(file);
    } else {
      onError(`File type not supported. Please upload ${allowedFileTypes.join(', ')} files.`);
      setSelectedFile(null);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      validateAndSetFile(file);
    }
  };

  const handleUploadClick = (e: MouseEvent<HTMLDivElement>) => {
    e.preventDefault();
    fileInputRef.current?.click();
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      onError('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      onStartProcessing();
      const response = await axios.post('http://localhost:5000/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      onFileProcessed(response.data);
    } catch (error: any) {
      let errorMessage = 'File processing failed. Please try again.';
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      }
      onError(errorMessage);
    }
  };

  return (
    <div className="file-upload-container">
      <h2>Upload Text Document</h2>

      <div
        className={`drop-zone ${dragActive ? 'active' : ''} ${selectedFile ? 'has-file' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleUploadClick}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".txt,.pdf,.docx"
          className="file-input"
          hidden
        />

        {selectedFile ? (
          <div className="file-info">
            <div className="file-icon">
              {/* file icon SVG */}
            </div>
            <div className="file-details">
              <p className="file-name">{selectedFile.name}</p>
              <p className="file-size">{(selectedFile.size / 1024).toFixed(2)} KB</p>
            </div>
          </div>
        ) : (
          <div className="upload-message">
            <div className="upload-icon">
              {/* upload icon SVG */}
            </div>
            <p>Drag & drop your file here or click to browse</p>
            <p className="supported-formats">
              Supported formats: {allowedFileTypes.join(', ')}
            </p>
          </div>
        )}
      </div>

      <button className="process-button" onClick={handleSubmit} disabled={!selectedFile}>
        Convert to Speech
      </button>
    </div>
  );
};

export default FileUpload;
