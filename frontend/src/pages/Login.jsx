
import { useState } from 'react';
import { login } from '../services/api';
import './Login.css';

function Login({ onLoginSuccess, onShowRegister }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    async function handleSubmit(event) {
        event.preventDefault();

        setError('');
        setLoading(true);

        try {
            await login(username, password);
            onLoginSuccess();
        } catch (err) {
            setError(err.message || 'Login failed. Please try again.');
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="login-container">
            <form className="login-card" onSubmit={handleSubmit}>
                <h1>AI Research Assistant</h1>
                <p>Sign in to continue your research.</p>

                <label htmlFor="username">Username</label>
                <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(event) => setUsername(event.target.value)}
                    placeholder="Enter your username"
                    autoComplete="username"
                    required
                />

                <label htmlFor="password">Password</label>
                <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    required
                />

                {error && <div className="login-error">{error}</div>}

                <button type="submit" disabled={loading}>
                    {loading ? 'Signing in...' : 'Login'}
                </button>
                <p className="register-login-link">
                Don't have an account?{' '}
                <button
                    type="button"
                    onClick={onShowRegister}
                >
                    Create account
                </button>
            </p>
            </form>
        </div>
    );
}

export default Login;
