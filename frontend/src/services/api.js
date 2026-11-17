
const API_BASE_URL = (
    import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
).replace(/\/+$/, '');

// Keep the JWT in memory, not localStorage.
let accessToken = null;

export function setAccessToken(token) {
    accessToken = token;
}

export function clearAccessToken() {
    accessToken = null;
}

async function request(endpoint, options = {}) {
    const headers = {
        ...options.headers,
    };

    // Attach JWT to protected API requests.
    if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
    }

    let response;

    try {
        response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers,
        });
    } catch {
        throw new Error(
            'Cannot connect to the backend. Check whether FastAPI is running.'
        );
    }

    if (response.status === 401) {
        clearAccessToken();
        window.dispatchEvent(new Event('auth:unauthorized'));
    }

    if (!response.ok) {
        let message = 'Something went wrong';

        try {
            const data = await response.json();
            message = data.detail || message;
        } catch {
            // Keep fallback message.
        }

        throw new Error(message);
    }

    if (response.status === 204) {
        return null;
    }

    const contentType = response.headers.get('content-type') || '';

    if (contentType.includes('application/json')) {
        return response.json();
    }

    return response.text();
}

// Registration endpoint uses JSON data.
export async function register(username, email, password) {
    return request('/auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username,
            email,
            password,
        }),
    });
}

// Login endpoint uses form-encoded data.
export async function login(username, password) {
    const formData = new URLSearchParams();

    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
    }

    setAccessToken(data.access_token);

    return data;
}

export async function getDocuments() {
    try {
        return await request('/all_documents');
    } catch (error) {
        if (error.message === 'Documents are empty') {
            return [];
        }
        throw error;
    }
}

export async function uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);

    return request('/api/v1/documents/upload', {
        method: 'POST',
        body: formData,
    });
}

export async function getDocument(documentId) {
    return request(`/get_document/${encodeURIComponent(documentId)}`);
}

export async function deleteDocument(documentId) {
    return request(`/documents/${encodeURIComponent(documentId)}`, {
        method: 'DELETE',
    });
}

export async function askQuestion(question, documentId = null) {
    return request('/api/v1/question-answer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question,
            document_id: documentId || null,
        }),
    });
}
