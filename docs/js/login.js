// If already logged in, skip straight to the dashboard.
if (Api.isLoggedIn()) {
  window.location.href = "/pages/dashboard.html";
}

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const rememberMe = document.getElementById("remember-me").checked;
  const btn = document.getElementById("login-btn");

  btn.disabled = true;
  btn.textContent = "Logging in...";

  try {
    const data = await Api.post("/login", { email, password, remember_me: rememberMe });
    Api.setSession(data.access_token, data.user_id, data.full_name);
    window.location.href = "/pages/dashboard.html";
  } catch (err) {
    showToast(err.message, true);
    btn.disabled = false;
    btn.textContent = "Log In";
  }
});
