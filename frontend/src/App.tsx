import './App.css';
import { useEffect, useState } from 'react';
import { uploadDocument, fetchDocuments, DocumentUploadResponse, deleteDocument } from './api/documents';
import UploadForm from './components/UploadForm';
import Sidebar from './components/Sidebar';

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [files, setFiles] = useState<DocumentUploadResponse[]>([]);
  const [status, setStatus] = useState('');

  const loadDocuments = async () => {
    try {
      const documents = await fetchDocuments();
      setFiles(documents);
    } catch (error) {
      setStatus((error as Error).message);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleFileChange = (selectedFile: File | null) => {
    setFile(selectedFile);
    setStatus('');
  };

  const handleUpload = async () => {
    if (!file) return setStatus('Please select a file to upload.');
    setStatus('Uploading...');

    try {
      const response = await uploadDocument(file);
      setStatus(`Uploaded: ${response.filename}`);
      await loadDocuments();
    } catch (error) {
      setStatus((error as Error).message);
    }
  };

  const handleDelete = async (documentId: number) => {
    try {
      await deleteDocument(documentId);
      await loadDocuments();
    } catch (error) {
      setStatus((error as Error).message);
    }
  };

  return (
    <div className="page-wrapper">
      <div className="home-container">
        <Sidebar files={files} onDelete={handleDelete} />

        <main className="main-panel">
          <div className="home-content">
            <h1>Clinical Document RAG Assistant</h1>
            <p>
              A document-based AI assistant that helps you search, analyze, and extract insights from clinical documents using retrieval-augmented generation.
            </p>
          </div>

          <UploadForm onFileChange={handleFileChange} onUpload={handleUpload} status={status} />
        </main>
      </div>
    </div>
  );
}

