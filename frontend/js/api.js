// Constants & Configuration
const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

// Token & Session Management Helpers
function getToken() {
    return localStorage.getItem("ecoquest_token");
}

function setToken(token) {
    localStorage.setItem("ecoquest_token", token);
}

function clearToken() {
    localStorage.removeItem("ecoquest_token");
}

function isAuthenticated() {
    const token = getToken();
    return token !== null && token.trim() !== "";
}

// Central HTTP Fetch Wrapper
async function request(endpoint, options = {}) {
    const url = API_BASE_URL + endpoint;
    const headers = options.headers || {};

    // Automatically set Content-Type unless handling FormData (file uploads)
    if (!(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    // Append Authorization header if token exists
    const token = getToken();
    if (token) {
        headers["Authorization"] = "Bearer " + token;
    }

    const config = {
        ...options,
        headers,
    };

    try {
        const response = await fetch(url, config);

        // Handle 401 Unauthorized
        if (response.status === 401) {
            clearToken();
            window.dispatchEvent(new Event("auth-expired"));
        }

        // Parse response JSON safely
        let data;
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            data = await response.json();
        } else {
            // Handle non-JSON responses
            const text = await response.text();
            data = text ? { detail: text } : {};
        }

        // Handle HTTP errors
        if (!response.ok) {
            const errorMessage = (data && data.detail) ? data.detail : (response.statusText || `HTTP Error ${response.status}`);
            throw new Error(errorMessage);
        }

        return data;
    } catch (error) {
        console.error("API Request Error:", error);
        throw error;
    }
}

// Exported Convenience Helper Methods
const api = {
    get: (endpoint) => {
        return request(endpoint, { method: "GET" });
    },
    
    post: (endpoint, body) => {
        return request(endpoint, {
            method: "POST",
            body: JSON.stringify(body),
        });
    },
    
    upload: (endpoint, formData) => {
        return request(endpoint, {
            method: "POST",
            body: formData,
        });
    }
};

export { api, getToken, setToken, clearToken, isAuthenticated };
