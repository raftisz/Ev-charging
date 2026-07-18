requireAuth();
renderSidebar("stations");

let allStations = [];

function renderStations(stations) {
  const grid = document.getElementById("station-grid");
  document.getElementById("results-count").textContent = `${stations.length} stations found nearby`;

  if (stations.length === 0) {
    grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1;">No stations match your search.</div>`;
    return;
  }

  grid.innerHTML = stations
    .map(
      (s, i) => `
      <a class="station-card" href="/pages/station-detail.html?id=${s.id}">
        <img src="${s.image_url}" alt="${s.name}" loading="lazy" />
        <div class="body">
          <div class="name-row">
            <div class="name">${s.name}</div>
            <span class="badge ${s.is_open ? "badge-green" : "badge-red"}">${s.is_open ? "Open" : "Closed"}</span>
          </div>
          <div class="meta-row">
            <span>📍 ${(1.2 + i * 0.3).toFixed(1)} km</span>
            <span>⭐ ${s.rating}</span>
            ${s.has_fast_charge ? '<span class="badge badge-blue">Fast Charge</span>' : ""}
          </div>
          <div class="name-row" style="margin-top:auto;">
            <span class="price">฿${s.price_per_kwh.toFixed(2)}<span style="font-size:11px; color:var(--text-1);">/kWh</span></span>
            <span class="text-dim" style="font-size:12px;">${s.opening_hours}</span>
          </div>
        </div>
      </a>`
    )
    .join("");
}

function applyFiltersAndSort() {
  const search = document.getElementById("search-input").value.toLowerCase();
  const fastOnly = document.getElementById("fast-charge-filter").checked;
  const sortBy = document.getElementById("sort-select").value;

  let filtered = allStations.filter((s) => s.name.toLowerCase().includes(search));
  if (fastOnly) filtered = filtered.filter((s) => s.has_fast_charge);

  if (sortBy === "price") filtered.sort((a, b) => a.price_per_kwh - b.price_per_kwh);
  if (sortBy === "rating") filtered.sort((a, b) => b.rating - a.rating);

  renderStations(filtered);
}

document.getElementById("search-input").addEventListener("input", applyFiltersAndSort);
document.getElementById("sort-select").addEventListener("change", applyFiltersAndSort);
document.getElementById("fast-charge-filter").addEventListener("change", applyFiltersAndSort);

(async function init() {
  try {
    allStations = await Api.get("/stations");
    applyFiltersAndSort();
  } catch (err) {
    showToast(err.message, true);
  }
})();
