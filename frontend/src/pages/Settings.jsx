
function Settings() {
    return (
        <div className="page">
            <div className="page-heading">
                <div>
                    <p className="eyebrow">PREFERENCES</p>
                    <h1>Settings</h1>
                    <p>Application information and connection status.</p>
                </div>
            </div>

            <section className="content-card">
                <h2>Application</h2>

                <div className="settings-row">
                    <span>Application name</span>
                    <strong>AI Research Assistant</strong>
                </div>

                <div className="settings-row">
                    <span>Frontend</span>
                    <strong>React + Vite</strong>
                </div>

                <div className="settings-row">
                    <span>Backend</span>
                    <strong>FastAPI</strong>
                </div>

                <div className="settings-row">
                    <span>API address</span>
                    <strong>http://127.0.0.1:8000</strong>
                </div>

                <div className="settings-row">
                    <span>Embedding model</span>
                    <strong>all-MiniLM-L6-v2</strong>
                </div>

                <div className="settings-row">
                    <span>Language model</span>
                    <strong>qwen2.5:3b-instruct</strong>
                </div>
            </section>
        </div>
    )
}

export default Settings
