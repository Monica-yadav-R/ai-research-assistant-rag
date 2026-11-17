
import { useState } from 'react'
import { askQuestion } from '../services/api'

function ResearchChat({ documents }) {
    const [question, setQuestion] = useState('')
    const [documentId, setDocumentId] = useState('')
    const [messages, setMessages] = useState([])
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState('')

    async function handleSubmit(event) {
        event.preventDefault()

        if (question.trim().length < 3 || isLoading) return

        const currentQuestion = question.trim()

        setMessages((previous) => [
            ...previous,
            { role: 'user', content: currentQuestion }
        ])

        setQuestion('')
        setError('')
        setIsLoading(true)

        try {
            const result = await askQuestion(
                currentQuestion,
                documentId || null
            )

            setMessages((previous) => [
                ...previous,
                {
                    role: 'assistant',
                    content: result.answer,
                    sources: result.sources || [],
                    limitations: result.limitations
                }
            ])
        } catch (err) {
            setError(err.message)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="page chat-page">
            <div className="page-heading">
                <div>
                    <p className="eyebrow">AI RESEARCH</p>
                    <h1>Research Chat</h1>
                    <p>Ask questions about your uploaded research papers.</p>
                </div>
            </div>

            <section className="content-card chat-container">
                <div className="chat-messages">
                    {messages.length === 0 && (
                        <div className="empty-state">
                            <h2>What would you like to research?</h2>
                            <p>
                                Ask a question about your documents.
                                Answers are generated using retrieved passages.
                            </p>
                        </div>
                    )}

                    {messages.map((message, index) => (
                        <div
                            className={`chat-message ${message.role}`}
                            key={index}
                        >
                            <strong>
                                {message.role === 'user' ? 'You' : 'Assistant'}
                            </strong>

                            <p>{message.content}</p>

                            {message.sources?.length > 0 && (
                                <div className="source-list">
                                    <strong>Sources</strong>

                                    {message.sources.map((source, i) => (
                                        <div key={`${source.source}-${source.page}-${i}`}>
                                            {source.source} — Page {source.page}
                                        </div>
                                    ))}
                                </div>
                            )}

                            {message.limitations && (
                                <p className="limitation-message">
                                    Limitation: {message.limitations}
                                </p>
                            )}
                        </div>
                    ))}

                    {isLoading && (
                        <p className="loading-message">
                            Researching your question...
                        </p>
                    )}
                </div>

                {error && <p className="error-message">{error}</p>}

                <form className="chat-form" onSubmit={handleSubmit}>
                    <select
                        value={documentId}
                        onChange={(event) =>
                            setDocumentId(event.target.value)
                        }
                    >
                        <option value="">Search all documents</option>
                        {documents.map((doc) => (
                            <option key={doc.id} value={doc.id}>
                                {doc.filename}
                            </option>
                        ))}
                    </select>

                    <textarea
                        value={question}
                        onChange={(event) => setQuestion(event.target.value)}
                        placeholder="Ask a research question..."
                        rows={3}
                    />

                    <button
                        className="primary-button"
                        type="submit"
                        disabled={isLoading || question.trim().length < 3}
                    >
                        {isLoading ? 'Thinking...' : 'Send question'}
                    </button>
                </form>
            </section>
        </div>
    )
}

export default ResearchChat
