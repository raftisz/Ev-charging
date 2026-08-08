requireAuth();
renderSidebar("profile");

async function loadProfile() {
  const profile = await Api.get("/profile");
  document.getElementById("profile-avatar").src = profile.avatar_url || "https://i.pravatar.cc/150";
  document.getElementById("profile-name").textContent = profile.full_name;
  document.getElementById("profile-email").textContent = profile.email;
  document.getElementById("full_name").value = profile.full_name;
  document.getElementById("phone").value = profile.phone || "";
  document.getElementById("dark_mode").checked = profile.dark_mode;
  document.getElementById("notifications").checked = profile.notifications_enabled;
}

async function loadVehicles() {
  const vehicles = await Api.get("/vehicles");
  const container = document.getElementById("vehicle-list");

  if (vehicles.length === 0) {
    container.innerHTML = `<div class="empty-state">No vehicles added yet.</div>`;
    return;
  }

  container.innerHTML = vehicles
    .map(
      (v) => `
      <div class="glass-panel" style="margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div style="font-weight:600;">${v.make} ${v.model} ${v.year ? `(${v.year})` : ""}</div>
          <div class="text-dim" style="font-size:12.5px;">${v.connector_type} · ${v.license_plate || "No plate"}</div>
        </div>
        ${v.is_default ? '<span class="badge badge-green">Default</span>' : ""}
      </div>`
    )
    .join("");
}

document.getElementById("profile-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = document.getElementById("save-profile-btn");
  btn.disabled = true;
  btn.textContent = "Saving...";

  try {
    await Api.put("/profile", {
      full_name: document.getElementById("full_name").value,
      phone: document.getElementById("phone").value,
      dark_mode: document.getElementById("dark_mode").checked,
      notifications_enabled: document.getElementById("notifications").checked,
    });
    localStorage.setItem("ev_full_name", document.getElementById("full_name").value);
    showToast("Profile updated.");
  } catch (err) {
    showToast(err.message, true);
  } finally {
    btn.disabled = false;
    btn.textContent = "Save Changes";
  }
});

document.getElementById("vehicle-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await Api.post("/vehicles", {
      make: document.getElementById("v_make").value,
      model: document.getElementById("v_model").value,
      year: document.getElementById("v_year").value ? Number(document.getElementById("v_year").value) : null,
      license_plate: document.getElementById("v_plate").value || null,
    });
    showToast("Vehicle added.");
    e.target.reset();
    loadVehicles();
  } catch (err) {
    showToast(err.message, true);
  }
});

(async function init() {
  try {
    await Promise.all([loadProfile(), loadVehicles()]);
  } catch (err) {
    showToast(err.message, true);
  }
})();
