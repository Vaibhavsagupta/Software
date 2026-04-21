const BASE_URL = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost" 
    ? "http://127.0.0.1:7070" 
    : "https://dental-erp-backend.onrender.com";

// 🔓 Security Removed: No auth headers needed
function getAuthHeader() {
    return {};
}

async function getData(url) {
    try {
        const res = await fetch(BASE_URL + url);
        return res.json();
    } catch (e) {
        console.error("Fetch Error:", e);
        return [];
    }
}

async function postData(url, data) {
    try {
        const res = await fetch(BASE_URL + url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    } catch (e) {
        console.error("Post Error:", e);
        return { error: e.message };
    }
}

async function putData(url, data = {}) {
    try {
        const res = await fetch(BASE_URL + url, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    } catch (e) {
        console.error("Put Error:", e);
        return { error: e.message };
    }
}

async function deleteData(url) {
    try {
        const res = await fetch(BASE_URL + url, {
            method: "DELETE"
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    } catch (e) {
        console.error("Delete Error:", e);
        return { error: e.message };
    }
}

// 🚪 Termination
function logout() {
    localStorage.clear();
    window.location.href = "login.html";
}

// 🌐 Navigation
function go(page) {
    window.location.href = page;
}
