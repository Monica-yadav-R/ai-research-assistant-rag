
function Dashboard({ documents, setActivePage }) {
    const processed = documents.filter(
        (doc) => doc.status === 'processed'
    ).length

    const recentDocuments = [...documents]
        .sort(
            (a, b) =>
                new Date(b.created_at) - new Date(a.created_at)
        )
        .slice(0, 5)

    return (
        <div className="page">
            <div className="page-heading">
                <div>
                    <p className="eyebrow">OVERVIEW</p>
                    <h1>Welcome to your Research Assistant</h1>
                    <p>Manage research papers and explore their contents.</p>
                </div>
                <button
                    className="primary-button"
                    onClick={() => setActivePage('documents')}
                >
                    + Upload PDF
                </button>
            </div>

            <div className="stats-grid">
                <div className="stat-card">
                    <span>Total documents</span>
                    <h2>{documents.length}</h2>
                </div>

                <div className="stat-card">
                    <span>Processed documents</span>
                    <h2>{processed}</h2>
                </div>

                <div className="stat-card">
                    <span>Total pages</span>
                    <h2>
                        {documents.reduce(
                            (total, doc) => total + doc.total_pages, 0
                        )}
                    </h2>
                </div>

                <div className="stat-card">
                    <span>Total chunks</span>
                    <h2>
                        {documents.reduce(
                            (total, doc) => total + doc.total_chunks, 0
                        )}
                    </h2>
                </div>
            </div>

            <section className="content-card">
                <div className="section-heading">
                    <h2>Recent documents</h2>
                    <button
                        className="text-button"
                        onClick={() => setActivePage('documents')}
                    >
                        View all
                    </button>
                </div>

                {recentDocuments.length === 0 ? (
                    <p className="empty-state">
                        No documents uploaded yet.
                    </p>
                ) : (
                    <div className="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Document</th>
                                    <th>Status</th>
                                    <th>Pages</th>
                                    <th>Chunks</th>
                                    <th>Uploaded</th>
                                </tr>
                            </thead>
                            <tbody>
                                {recentDocuments.map((doc) => (
                                    <tr key={doc.id}>
                                        <td>{doc.filename}</td>
                                        <td>
                                            <span className="status-badge">
                                                {doc.status}
                                            </span>
                                        </td>
                                        <td>{doc.total_pages}</td>
                                        <td>{doc.total_chunks}</td>
                                        <td>
                                            {new Date(
                                                doc.created_at
                                            ).toLocaleDateString()}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </section>
        </div>
    )
}

export default Dashboard
