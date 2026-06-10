import { DocumentUploadResponse } from '../api/documents';

interface SidebarProps {
  files: DocumentUploadResponse[];
}

export default function Sidebar({ files }: SidebarProps) {
  return (
    <aside className="sidebar">
      <h2>Uploaded Files</h2>
      <ul className="file-list">
        {files.length > 0 ? (
          files.map((document) => (
            <li key={document.id} className="file-list-item">
              {document.filename}
            </li>
          ))
        ) : (
          <li className="file-list-empty">No files uploaded yet.</li>
        )}
      </ul>
    </aside>
  );
}
