requireAuth();
renderSidebar("dashboard");

const RING_CIRCUMFERENCE = 490;

function setRing(percent) {
  const offset = RING_CIRCUMFERENCE - (RING_CIRCUMFERENCE * percent) / 100;
  document.getElementById("ring-progress").style.strokeDashoffset = offset;
  document.getElementById("battery-pct").textContent = `${percent}%`;
}

function formatCurrency(amount) {
  return `฿${Number(amount).toFixed(2)}`;
}

async function loadProfile() {
  const profile = await Api.get("/profile");
  document.getElementById("greeting").textContent = `Hi, ${profile.full_name.split(" ")[0]} 👋`;
  document.getElementById("stat-wallet").textContent = formatCurrency(profile.wallet_balance);
  document.getElementById("stat-points").innerHTML = `${profile.reward_points} <small>pts</small>`;
}

async function loadChargingStatus() {
  try {
    const session = await Api.get("/charging/status");
    setRing(session.battery_percent);
    const label = session.status === "charging" ? "Charging now" : session.status === "completed" ? "Fully charged" : "Session stopped";
    document.getElementById("battery-status").textContent = label;
  } catch (e) {
    setRing(0);
    document.getElementById("battery-status").textContent = "No active session";
  }
}

async function loadCurrentReservation() {
  const bookings = await Api.get("/bookings");
  const upcoming = bookings.find((b) => b.status === "confirmed");
  const container = document.getElementById("current-reservation");

  if (!upcoming) return; // keep the empty state markup already in the page

  const stations = await Api.get("/stations");
  const station = stations.find((s) => s.id === upcoming.station_id);

  container.innerHTML = `
    <div class="glass-panel">
      <div class="badge badge-green" style="margin-bottom:10px;">Confirmed</div>
      <h4 style="margin-bottom:6px;">${station ? station.name : "Charging Station"}</h4>
      <div class="text-muted" style="font-size:13.5px; margin-bottom:14px;">
        ${upcoming.reservation_date} at ${upcoming.reservation_time}
      </div>
      <div class="text-muted" style="font-size:13px; margin-bottom:16px;">
        Estimated cost: <strong style="color:var(--text-0);">${formatCurrency(upcoming.estimated_cost)}</strong>
      </div>
      <a class="btn btn-primary" href="/pages/charging-status.html">Start Charging</a>
    </div>`;

  document.getElementById("stat-sessions").textContent = bookings.length;
}

async function loadFavorites() {
  const [favorites, stations] = await Promise.all([Api.get("/favorites"), Api.get("/stations")]);
  const container = document.getElementById("favorite-stations");

  const favoriteStations = favorites
    .map((f) => stations.find((s) => s.id === f.station_id))
    .filter(Boolean)
    .slice(0, 4);

  if (favoriteStations.length === 0) {
    container.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">No favorite stations yet.</div>`;
    return;
  }

  container.innerHTML = favoriteStations
    .map(
      (s) => `
      <a href="/pages/station-detail.html?id=${s.id}" class="glass-panel" style="display:block;">
        <div style="font-weight:600; font-size:14px; margin-bottom:4px;">${s.name}</div>
        <div class="text-dim" style="font-size:12px;">${s.address}</div>
      </a>`
    )
    .join("");
}

async function loadRecentHistory() {
  const payments = await Api.get("/payments");
  const container = document.getElementById("recent-history");

  if (payments.length === 0) {
    container.innerHTML = `<div class="empty-state">No charging history yet.</div>`;
    return;
  }

  container.innerHTML = payments
    .slice(0, 4)
    .map(
      (p) => `
      <div class="history-row">
        <div>
          <div class="title">Charging Session</div>
          <div class="sub">${new Date(p.created_at).toLocaleDateString()}</div>
        </div>
        <div>${p.method.replace("_", " ")}</div>
        <div class="badge badge-green">Paid</div>
        <div style="text-align:right; font-weight:600;">${formatCurrency(p.amount)}</div>
      </div>`
    )
    .join("");
}

(async function init() {
  try {
    await Promise.all([
      loadProfile(),
      loadChargingStatus(),
      loadCurrentReservation(),
      loadFavorites(),
      loadRecentHistory(),
    ]);
  } catch (err) {
    showToast(err.message, true);
  }
})();
