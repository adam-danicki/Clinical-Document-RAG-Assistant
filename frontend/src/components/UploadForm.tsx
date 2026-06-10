import { useState } from 'react';

interface UploadFormProps {
  onFileChange: (file: File | null) => void;
  onUpload: () => void;
  status?: string;
}

export default function UploadForm({ onFileChange, onUpload, status }: UploadFormProps) {
  const [fileName, setFileName] = useState('');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0] ?? null;
    setFileName(selectedFile?.name ?? '');
    onFileChange(selectedFile);
  };

  return (
    <div className="upload-card">
      <h2>Upload PDF</h2>
      <div className="upload-actions">
        <label className="file-picker">
          <input type="file" accept="application/pdf" onChange={handleFileChange} />
          <span>Select PDF</span>
        </label>
        <button type="button" onClick={onUpload} className="submit-button">
          Submit
        </button>
      </div>
      {fileName && <p className="selected-file">Selected file: {fileName}</p>}
      {status && <p className="status-text">{status}</p>}
    </div>
  );
}
