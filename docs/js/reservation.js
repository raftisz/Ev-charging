requireAuth();
renderSidebar("reservation");

const ESTIMATED_KWH = 40;
let currentStation = null;

function getStationIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get("station_id");
}

function updateSummary() {
  if (!currentStation) return;

  const date = document.getElementById("date").value || "—";
  const time = document.getElementById("time").value || "—";
  const chargerSelect = document.getElementById("charger");
  const chargerLabel = chargerSelect.options[chargerSelect.selectedIndex]
    ? chargerSelect.options[chargerSelect.selectedIndex].text
    : "—";
  const estimatedCost = (currentStation.price_per_kwh * ESTIMATED_KWH).toFixed(2);

  document.getElementById("summary-body").innerHTML = `
    <div class="glass-panel">
      <div style="font-weight:600; margin-bottom:4px;">${currentStation.name}</div>
      <div class="text-dim" style="font-size:12.5px; margin-bottom:16px;">${currentStation.address}</div>

      <div class="history-row" style="grid-template-columns:1fr auto;">
        <div class="text-muted">Date</div><div>${date}</div>
      </div>
      <div class="history-row" style="grid-template-columns:1fr auto;">
        <div class="text-muted">Time</div><div>${time}</div>
      </div>
      <div class="history-row" style="grid-template-columns:1fr auto;">
        <div class="text-muted">Charger</div><div>${chargerLabel}</div>
      </div>
      <div class="history-row" style="grid-template-columns:1fr auto;">
        <div class="text-muted">Price per kWh</div><div>฿${currentStation.price_per_kwh.toFixed(2)}</div>
      </div>
      <div class="history-row" style="grid-template-columns:1fr auto; border-bottom:none;">
        <div style="font-weight:600;">Estimated Cost</div><div style="font-weight:700; color:var(--green);">฿${estimatedCost}</div>
      </div>
    </div>`;
}

async function loadVehicles() {
  const vehicles = await Api.get("/vehicles");
  const select = document.getElementById("vehicle");
  if (vehicles.length === 0) {
    select.innerHTML = `<option value="">No vehicle on file</option>`;
    return;
  }
  select.innerHTML = vehicles
    .map((v) => `<option value="${v.id}">${v.make} ${v.model} (${v.license_plate || "no plate"})</option>`)
    .join("");
}

async function loadStation(stationId) {
  currentStation = await Api.get(`/stations/${stationId}`);
  document.getElementById("station-name-sub").textContent = `Reserving at ${currentStation.name}`;

  const chargerSelect = document.getElementById("charger");
  const available = currentStation.chargers.filter((c) => c.is_available);
  const source = available.length > 0 ? available : currentStation.chargers;

  chargerSelect.innerHTML = source
    .map((c) => `<option value="${c.id}">${c.charger_code} · ${c.connector_type} · ${c.power_kw} kW</option>`)
    .join("");

  updateSummary();
}

document.getElementById("date").addEventListener("change", updateSummary);
document.getElementById("time").addEventListener("change", updateSummary);
document.getElementById("charger").addEventListener("change", updateSummary);

document.getElementById("reservation-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!currentStation) {
    showToast("Please choose a station first from the Stations page.", true);
    return;
  }

  const btn = document.getElementById("confirm-btn");
  btn.disabled = true;
  btn.textContent = "Confirming...";

  try {
    const vehicleSelect = document.getElementById("vehicle");
    await Api.post("/bookings", {
      station_id: currentStation.id,
      charger_id: Number(document.getElementById("charger").value),
      vehicle_id: vehicleSelect.value ? Number(vehicleSelect.value) : null,
      reservation_date: document.getElementById("date").value,
      reservation_time: document.getElementById("time").value,
    });
    showToast("Reservation confirmed!");
    setTimeout(() => (window.location.href = "/pages/charging-status.html"), 900);
  } catch (err) {
    showToast(err.message, true);
    btn.disabled = false;
    btn.textContent = "Confirm Reservation";
  }
});

(async function init() {
  const today = new Date().toISOString().split("T")[0];
  document.getElementById("date").value = today;
  document.getElementById("date").min = today;

  try {
    await loadVehicles();
    const stationId = getStationIdFromUrl();
    if (stationId) {
      await loadStation(stationId);
    }
  } catch (err) {
    showToast(err.message, true);
  }
})();
