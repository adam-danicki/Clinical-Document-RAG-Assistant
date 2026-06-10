import { DocumentUploadResponse } from '../api/documents';
import { useState } from 'react';

interface SidebarProps {
  files: DocumentUploadResponse[];
  onDelete: (documentId: number) => Promise<void>;
}

export default function Sidebar({ files, onDelete }: SidebarProps) {
  const [deleting, setDeleting] = useState<number | null>(null);
  const [error, setError] = useState<string>('');

  async function handleDelete(documentId: number) {
    setDeleting(documentId);
    setError('');

    try {
      await onDelete(documentId);
    } catch (error) {
      setError((error as Error).message);
    } finally {
      setDeleting(null);
    }
  }

  return (
    <aside className="sidebar">
      <h2>Uploaded Files</h2>

      <ul className="file-list">
        {files.length > 0 ? (
          files.map((document) => (
            <li key={document.id} className="file-list-item">
              <div className="file-item-content">
                <span>{document.filename}</span>

                <button
                  className="delete-button"
                  type="button"
                  onClick={() => handleDelete(Number(document.id))}
                  disabled={deleting === Number(document.id)}
                  title="Delete file"
                >
                  {deleting === Number(document.id) ? '...' : '×'}
                </button>
              </div>
            </li>
          ))
        ) : (
          <li className="file-list-empty">No files uploaded yet.</li>
        )}
      </ul>

      {error && <div className="error-message">{error}</div>}
    </aside>
  );
}