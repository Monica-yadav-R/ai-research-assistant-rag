
import { useState } from 'react';
import './Register.css';
import { register } from '../services/api';

function Register({ onShowLogin }) {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState('');

    async function handleSubmit(event) {
        event.preventDefault();

        setError('');
        setSuccess('');

        if (password !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }

        try {
            setLoading(true);

            await register(username, email, password);

            setSuccess('Account created successfully! You can now log in.');

            setUsername('');
            setEmail('');
            setPassword('');
            setConfirmPassword('');
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="register-container">
            <form className="register-card" onSubmit={handleSubmit}>
                <h1>Create Account</h1>
                <p>Join AI Research Assistant.</p>

                <label htmlFor="register-username">Username</label>
                <input
                    id="register-username"
                    type="text"
                    value={username}
                    onChange={(event) => setUsername(event.target.value)}
                    placeholder="Enter username"
                    autoComplete="username"
                    required
                />

                <label htmlFor="register-email">Email</label>
                <input
                    id="register-email"
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    placeholder="Enter email address"
                    autoComplete="email"
                    required
                />

                <label htmlFor="register-password">Password</label>
                <input
                    id="register-password"
                    type="password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Create password"
                    autoComplete="new-password"
                    required
                />

                <label htmlFor="confirm-password">
                    Confirm Password
                </label>
                <input
                    id="confirm-password"
                    type="password"
                    value={confirmPassword}
                    onChange={(event) => setConfirmPassword(event.target.value)}
                    placeholder="Confirm password"
                    autoComplete="new-password"
                    required
                />

                {error && (
                    <div className="register-error">{error}</div>
                )}

                {success && (
                    <div className="register-success">{success}</div>
                )}

                <button type="submit" disabled={loading}>
                    {loading ? 'Creating Account...' : 'Create Account'}
                </button>

                <p className="register-login-link">
                    Already have an account?{' '}
                    <button type="button" onClick={onShowLogin}>
                        Login
                    </button>
                </p>
            </form>
        </div>
    );
}

export default Register;
