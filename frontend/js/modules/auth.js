import { api, setToken, clearToken, isAuthenticated } from "../api.js";

// Ensure we have access to the same API_BASE_URL used in api.js
const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

function updateAuthUI() {
    const authCard = document.getElementById("authCard");
    const appDashboard = document.getElementById("appDashboard");
    const userInfo = document.getElementById("userInfo");

    if (isAuthenticated()) {
        if (authCard) authCard.style.display = "none";
        if (appDashboard) appDashboard.style.display = "block";
        if (userInfo) userInfo.textContent = "Session Active";
    } else {
        if (authCard) authCard.style.display = "block";
        if (appDashboard) appDashboard.style.display = "none";
        if (userInfo) userInfo.textContent = "Not Logged In";
    }
}

async function handleRegister(email, password) {
    if (!email || !password) {
        alert("Email and password are required.");
        return;
    }
    
    try {
        await api.post("/auth/register", { email, password });
        alert("Registration successful! Please log in.");
    } catch (error) {
        console.error("Registration Error:", error);
        alert("Registration failed: " + error.message);
    }
}

async function handleLogin(email, password) {
    if (!email || !password) {
        alert("Email and password are required.");
        return;
    }

    // Convert credentials into URLSearchParams for OAuth2PasswordRequestForm compatibility
    const params = new URLSearchParams();
    params.append("username", email);
    params.append("password", password);

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: params.toString(),
        });

        if (!response.ok) {
            let errorMsg = "Login failed";
            try {
                const data = await response.json();
                errorMsg = data.detail || errorMsg;
            } catch (e) {
                errorMsg = response.statusText;
            }
            throw new Error(errorMsg);
        }

        const data = await response.json();
        
        // Save the access_token 
        setToken(data.access_token);
        
        // Update UI and notify application
        updateAuthUI();
        window.dispatchEvent(new Event("user-logged-in"));
    } catch (error) {
        console.error("Login Error:", error);
        alert("Login failed: " + error.message);
    }
}

function handleLogout() {
    clearToken();
    updateAuthUI();
    window.dispatchEvent(new Event("user-logged-out"));
}

function initAuth() {
    const registerBtn = document.getElementById("registerBtn");
    const loginBtn = document.getElementById("loginBtn");
    const logoutBtn = document.getElementById("logoutBtn");

    if (registerBtn) {
        registerBtn.addEventListener("click", (e) => {
            e.preventDefault();
            const email = document.getElementById("authEmail")?.value;
            const password = document.getElementById("authPassword")?.value;
            handleRegister(email, password);
        });
    }

    if (loginBtn) {
        loginBtn.addEventListener("click", (e) => {
            e.preventDefault();
            const email = document.getElementById("authEmail")?.value;
            const password = document.getElementById("authPassword")?.value;
            handleLogin(email, password);
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener("click", (e) => {
            e.preventDefault();
            handleLogout();
        });
    }

    // Listen for auth-expired event dispatched by api.js
    window.addEventListener("auth-expired", () => {
        alert("Session expired. Please log in again.");
        updateAuthUI();
    });
    
    // Set initial UI state based on current authentication status
    updateAuthUI();
}

export { initAuth, handleRegister, handleLogin, handleLogout, updateAuthUI };
