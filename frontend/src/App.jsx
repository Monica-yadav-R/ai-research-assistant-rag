
import { useCallback, useEffect, useState } from 'react';

import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import ResearchChat from './pages/ResearchChat';
import Settings from './pages/Settings';
import Login from './pages/Login';
import Register from './pages/Register';

import {
    getDocuments,
    clearAccessToken,
} from './services/api';

import './App.css';

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [showRegister, setShowRegister] = useState(false);

    const [activePage, setActivePage] = useState('dashboard');
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const refreshDocuments = useCallback(async () => {
        try {
            const data = await getDocuments();
            setDocuments(data);
            setError('');
        } catch (err) {
            setError(err.message);
        }
    }, []);

    useEffect(() => {
        function handleUnauthorized() {
            clearAccessToken();
            setIsAuthenticated(false);
            setDocuments([]);
            setError('Your session has expired. Please log in again.');
        }

        window.addEventListener(
            'auth:unauthorized',
            handleUnauthorized
        );

        return () => {
            window.removeEventListener(
                'auth:unauthorized',
                handleUnauthorized
            );
        };
    }, []);

    async function handleLoginSuccess() {
        setError('');
        setIsAuthenticated(true);
        setLoading(true);

        try {
            await refreshDocuments();
        } finally {
            setLoading(false);
        }
    }

    function handleLogout() {
        clearAccessToken();
        setIsAuthenticated(false);
        setDocuments([]);
        setActivePage('dashboard');
        setShowRegister(false);
        setError('');
    }

    function renderPage() {
        if (loading) {
            return <div className="page">Loading...</div>;
        }

        if (activePage === 'dashboard') {
            return (
                <Dashboard
                    documents={documents}
                    setActivePage={setActivePage}
                />
            );
        }

        if (activePage === 'documents') {
            return (
                <Documents
                    documents={documents}
                    setDocuments={setDocuments}
                    refreshDocuments={refreshDocuments}
                />
            );
        }

        if (activePage === 'chat') {
            return <ResearchChat documents={documents} />;
        }

        if (activePage === 'settings') {
            return <Settings />;
        }

        return (
            <Dashboard
                documents={documents}
                setActivePage={setActivePage}
            />
        );
    }

    if (!isAuthenticated) {
        if (showRegister) {
            return (
                <Register
                    onShowLogin={() => setShowRegister(false)}
                />
            );
        }

        return (
            <Login
                onLoginSuccess={handleLoginSuccess}
                onShowRegister={() => setShowRegister(true)}
            />
        );
    }

    return (
        <div className="app-layout">
            <Sidebar
                activePage={activePage}
                setActivePage={setActivePage}
            />

            <main className="main-area">
                <div className="global-actions">
                    <button onClick={handleLogout}>
                        Logout
                    </button>
                </div>

                {error && (
                    <div className="global-error">
                        {error}
                        <button onClick={refreshDocuments}>
                            Retry
                        </button>
                    </div>
                )}

                {renderPage()}
            </main>
        </div>
    );
}

export default App;
