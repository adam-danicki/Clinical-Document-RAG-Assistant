const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

// Define the structure of the response from the /documents/upload endpoint
export interface DocumentUploadResponse {
  id: string;
  filename: string;
  message?: string;
}

// Define the structure of the response from the /documents/ask endpoint
export interface AskResponse {
  answer: string;
  sources?: Array<{ documentId: string; preview: string }>;
}

// Fetch all uploaded documents
export async function fetchDocuments(): Promise<DocumentUploadResponse[]> {
  const response = await fetch(`${API_BASE}/documents`);
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to fetch documents: ${response.status} ${errorText}`);
  }

  const data = await response.json();
  return data.documents ?? [];
}

// Fetch a single document by ID
export async function fetchDocument(documentId: number): Promise<DocumentUploadResponse> {
  const response = await fetch(`${API_BASE}/documents/${documentId}`);
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to fetch document: ${response.status} ${errorText}`);
  }
  return response.json();
}

// Upload a document file to the backend
export async function uploadDocument(file: File): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Upload failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

// Ask a question and get an answer based on the uploaded documents
export async function askQuestion(question: string): Promise<AskResponse> {
  const response = await fetch(`${API_BASE}/documents/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Ask failed: ${response.status} ${errorText}`);
  }

  return response.json();
}
