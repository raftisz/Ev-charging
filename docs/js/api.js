/**
 * Shared API client. Every page includes this before its own script.
 * Wraps fetch() with the base URL, JSON handling, and JWT auth header.
 */

const API_BASE = "/api";

const Api = {
  getToken() {
    return localStorage.getItem("ev_token");
  },

  setSession(token, userId, fullName) {
    localStorage.setItem("ev_token", token);
    localStorage.setItem("ev_user_id", userId);
    localStorage.setItem("ev_full_name", fullName);
  },

  clearSession() {
    localStorage.removeItem("ev_token");
    localStorage.removeItem("ev_user_id");
    localStorage.removeItem("ev_full_name");
  },

  isLoggedIn() {
    return Boolean(this.getToken());
  },

  async request(path, options = {}) {
    const headers = Object.assign(
      { "Content-Type": "application/json" },
      options.headers || {}
    );

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    if (response.status === 401) {
      this.clearSession();
      window.location.href = "/pages/login.html";
      return Promise.reject(new Error("Session expired"));
    }

    let data = null;
    try {
      data = await response.json();
    } catch (e) {
      data = null;
    }

    if (!response.ok) {
      const message = (data && data.detail) || "Something went wrong. Please try again.";
      throw new Error(message);
    }

    return data;
  },

  get(path) {
    return this.request(path, { method: "GET" });
  },
  post(path, body) {
    return this.request(path, { method: "POST", body });
  },
  put(path, body) {
    return this.request(path, { method: "PUT", body });
  },
};

/** Redirect to login if there is no active session. Call at top of protected pages. */
function requireAuth() {
  if (!Api.isLoggedIn()) {
    window.location.href = "/pages/login.html";
  }
}

/** Show a small toast message at the bottom of the screen. */
function showToast(message, isError = false) {
  let toast = document.getElementById("toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("show");
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove("show"), 3200);
}

function logout() {
  Api.clearSession();
  window.location.href = "/pages/login.html";
}
