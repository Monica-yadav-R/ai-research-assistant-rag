
import { useMemo, useState } from 'react'
import {  uploadDocument } from '../services/api'

const MAX_FILE_SIZE = 10 * 1024 * 1024

function Documents({ documents, setDocuments, refreshDocuments }) {
    const [selectedFile, setSelectedFile] = useState(null)
    const [searchQuery, setSearchQuery] = useState('')
    const [isUploading, setIsUploading] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')

    const filteredDocuments = useMemo(() => {
        return documents.filter((doc) =>
            doc.filename.toLowerCase().includes(
                searchQuery.toLowerCase()
            )
        )
    }, [documents, searchQuery])

    function handleFileChange(event) {
        const file = event.target.files?.[0]

        setError('')
        setSuccess('')

        if (!file) {
            setSelectedFile(null)
            return
        }

        if (
            file.type !== 'application/pdf' &&
            !file.name.toLowerCase().endsWith('.pdf')
        ) {
            setSelectedFile(null)
            setError('Please select a valid PDF file.')
            return
        }

        if (file.size > MAX_FILE_SIZE) {
            setSelectedFile(null)
            setError('File size must not exceed 10 MB.')
            return
        }

        setSelectedFile(file)
    }

    async function handleUpload() {
        if (!selectedFile) return

        setIsUploading(true)
        setError('')
        setSuccess('')

        try {
            const result = await uploadDocument(selectedFile)

            setSuccess(result.message)
            setSelectedFile(null)

            await refreshDocuments()
        } catch (err) {
            setError(err.message)
        } finally {
            setIsUploading(false)
        }
    }

    return (
        <div className="page">
            <div className="page-heading">
                <div>
                    <p className="eyebrow">LIBRARY</p>
                    <h1>My Documents</h1>
                    <p>Upload and manage your research papers.</p>
                </div>
            </div>

            <section className="content-card upload-card">
                <h2>Upload research paper</h2>
                <p>Choose a PDF file up to 10 MB.</p>

                <input
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={handleFileChange}
                />

                {selectedFile && (
                    <p className="selected-file">
                        Selected: {selectedFile.name}
                    </p>
                )}

                {error && <p className="error-message">{error}</p>}
                {success && <p className="success-message">{success}</p>}

                <button
                    className="primary-button"
                    onClick={handleUpload}
                    disabled={!selectedFile || isUploading}
                >
                    {isUploading ? 'Processing PDF...' : 'Upload PDF'}
                </button>
            </section>

            <section className="content-card">
                <div className="section-heading">
                    <div>
                        <h2>Uploaded documents</h2>
                        <p>{documents.length} documents</p>
                    </div>

                    <input
                        className="search-input"
                        type="search"
                        placeholder="Search by filename..."
                        value={searchQuery}
                        onChange={(event) =>
                            setSearchQuery(event.target.value)
                        }
                    />
                </div>

                {filteredDocuments.length === 0 ? (
                    <p className="empty-state">
                        {searchQuery
                            ? 'No matching documents found.'
                            : 'No documents uploaded yet.'}
                    </p>
                ) : (
                    <div className="document-grid">
                        {filteredDocuments.map((doc) => (
                            <article className="document-card" key={doc.id}>
                                <div className="document-card-top">
                                    <span className="pdf-icon">PDF</span>
                                    <span className="status-badge">
                                        {doc.status}
                                    </span>
                                </div>

                                <h3>{doc.filename}</h3>

                                <div className="document-metadata">
                                    <span>{doc.total_pages} pages</span>
                                    <span>{doc.total_chunks} chunks</span>
                                </div>

                                <p className="document-date">
                                    Uploaded: {new Date(
                                        doc.created_at
                                    ).toLocaleDateString()}
                                </p>

                                {doc.error_message && (
                                    <p className="error-message">
                                        {doc.error_message}
                                    </p>
                                )}
                            </article>
                        ))}
                    </div>
                )}
            </section>
        </div>
    )
}

export default Documents
