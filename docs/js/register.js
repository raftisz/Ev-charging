if (Api.isLoggedIn()) {
  window.location.href = "/pages/dashboard.html";
}

document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const full_name = document.getElementById("full_name").value.trim();
  const email = document.getElementById("email").value.trim();
  const phone = document.getElementById("phone").value.trim();
  const password = document.getElementById("password").value;
  const confirm_password = document.getElementById("confirm_password").value;
  const btn = document.getElementById("register-btn");

  if (password !== confirm_password) {
    showToast("Passwords do not match", true);
    return;
  }

  btn.disabled = true;
  btn.textContent = "Creating account...";

  try {
    const data = await Api.post("/register", {
      full_name,
      email,
      phone: phone || null,
      password,
      confirm_password,
    });
    Api.setSession(data.access_token, data.user_id, data.full_name);
    window.location.href = "/pages/dashboard.html";
  } catch (err) {
    showToast(err.message, true);
    btn.disabled = false;
    btn.textContent = "Create Account";
  }
});
