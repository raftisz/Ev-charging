requireAuth();
renderSidebar("charging");

const RING_CIRCUMFERENCE = 490;
let pollTimer = null;

function renderContent(session) {
  const percent = session.battery_percent;
  const offsetReady = RING_CIRCUMFERENCE - (RING_CIRCUMFERENCE * percent) / 100;
  const isCharging = session.status === "charging";

  document.getElementById("status-label").textContent =
    session.status === "charging" ? "Charging in progress" : session.status === "completed" ? "Charging complete" : "Session stopped";
  document.getElementById("live-dot").style.background = isCharging ? "var(--green)" : "var(--text-2)";

  document.getElementById("charging-content").innerHTML = `
    <div class="grid grid-2" style="align-items:start;">
      <div class="glass-card" style="display:flex; flex-direction:column; align-items:center;">
        <div class="charge-ring-wrap" style="margin:10px 0 18px;">
          <div class="charge-ring">
            <svg width="220" height="220" viewBox="0 0 180 180">
              <defs>
                <linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#2fe6a0" />
                  <stop offset="100%" stop-color="#3fa9ff" />
                </linearGradient>
              </defs>
              <circle class="ring-track" cx="90" cy="90" r="78" stroke-width="14" fill="none" />
              <circle class="ring-progress" cx="90" cy="90" r="78" stroke-width="14" fill="none"
                stroke-dasharray="${RING_CIRCUMFERENCE}" stroke-dashoffset="${offsetReady}" />
            </svg>
          </div>
          <div class="charge-ring-center">
            <div class="pct">${percent}%</div>
            <div class="label">Battery Level</div>
          </div>
        </div>
        <button class="btn btn-danger btn-block" id="stop-btn" ${isCharging ? "" : "disabled"}>
          ${isCharging ? "Stop Charging" : "Session Ended"}
        </button>
      </div>

      <div class="glass-card">
        <h3 style="margin-bottom:16px;">Session Details</h3>
        <div class="grid grid-2">
          <div class="stat-tile"><div class="stat-label">Charging Progress</div><div class="stat-value" style="font-size:20px;">${session.charging_progress}%</div></div>
          <div class="stat-tile"><div class="stat-label">Power Output</div><div class="stat-value" style="font-size:20px;">${session.power_output_kw} kW</div></div>
          <div class="stat-tile"><div class="stat-label">Charging Speed</div><div class="stat-value" style="font-size:20px;">${session.charging_speed}</div></div>
          <div class="stat-tile"><div class="stat-label">Remaining Time</div><div class="stat-value" style="font-size:20px;">${session.remaining_minutes} min</div></div>
        </div>
        <div class="glass-panel" style="margin-top:18px; display:flex; justify-content:space-between; align-items:center;">
          <span class="text-muted">Current Cost</span>
          <span style="font-family:var(--font-display); font-size:22px; color:var(--green);">฿${session.current_cost.toFixed(2)}</span>
        </div>
        ${session.status !== "charging" ? `<a class="btn btn-primary" style="margin-top:18px;" href="/pages/payment.html">Proceed to Payment</a>` : ""}
      </div>
    </div>`;

  const stopBtn = document.getElementById("stop-btn");
  if (stopBtn && isCharging) {
    stopBtn.addEventListener("click", stopCharging);
  }
}

async function stopCharging() {
  try {
    const session = await Api.post("/charging/stop", {});
    clearInterval(pollTimer);
    renderContent(session);
    showToast("Charging stopped.");
  } catch (err) {
    showToast(err.message, true);
  }
}

async function pollStatus() {
  try {
    const session = await Api.get("/charging/status");
    renderContent(session);
    if (session.status !== "charging") clearInterval(pollTimer);
  } catch (err) {
    document.getElementById("charging-content").innerHTML = `
      <div class="empty-state">
        <div class="icon">🔌</div>
        No active charging session.
        <div style="margin-top:14px;"><a class="btn btn-primary" style="width:auto; display:inline-flex;" href="/pages/stations.html">Reserve a Charger</a></div>
      </div>`;
    document.getElementById("status-label").textContent = "No active session";
    document.getElementById("live-dot").style.background = "var(--text-2)";
    clearInterval(pollTimer);
  }
}

(async function init() {
  await pollStatus();
  pollTimer = setInterval(pollStatus, 4000);
})();
