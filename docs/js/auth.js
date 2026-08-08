/**
 * Renders the shared sidebar navigation into <div id="sidebar-root">
 * and wires up the mobile menu toggle + logout button.
 * Include after api.js on every authenticated page.
 */

const NAV_ITEMS = [
  { href: "/pages/dashboard.html", label: "Dashboard", key: "dashboard", icon: "grid" },
  { href: "/pages/stations.html", label: "Find Stations", key: "stations", icon: "pin" },
  { href: "/pages/reservation.html", label: "Reservations", key: "reservation", icon: "calendar" },
  { href: "/pages/charging-status.html", label: "Charging Status", key: "charging", icon: "bolt" },
  { href: "/pages/history.html", label: "History", key: "history", icon: "clock" },
  { href: "/pages/profile.html", label: "Profile", key: "profile", icon: "user" },
];

const ICONS = {
  grid: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="8" height="8" rx="2"/><rect x="13" y="3" width="8" height="8" rx="2"/><rect x="3" y="13" width="8" height="8" rx="2"/><rect x="13" y="13" width="8" height="8" rx="2"/></svg>',
  pin: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11Z"/><circle cx="12" cy="10" r="2.5"/></svg>',
  calendar: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
  bolt: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M13 2 4 14h6l-1 8 9-12h-6l1-8Z"/></svg>',
  clock: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>',
  user: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="8" r="4"/><path d="M4 20c1.8-4 5-6 8-6s6.2 2 8 6"/></svg>',
};

function renderSidebar(activeKey) {
  const root = document.getElementById("sidebar-root");
  if (!root) return;

  const fullName = localStorage.getItem("ev_full_name") || "EV Driver";

  const links = NAV_ITEMS.map(
    (item) => `
      <a class="nav-link ${item.key === activeKey ? "active" : ""}" href="${item.href}">
        ${ICONS[item.icon]}
        <span>${item.label}</span>
      </a>`
  ).join("");

  root.innerHTML = `
    <aside class="sidebar" id="sidebar">
      <div class="brand">
        <div class="brand-mark">V</div>
        <div class="brand-name">Volt Grid</div>
      </div>
      <div class="nav-group">
        <div class="nav-section-label">Menu</div>
        ${links}
      </div>
      <div class="sidebar-footer">
        <div style="display:flex; align-items:center; gap:10px; padding:8px 4px 14px;">
          <div class="brand-mark" style="background:var(--glass); color:var(--text-0); border:1px solid var(--glass-border);">
            ${fullName.charAt(0).toUpperCase()}
          </div>
          <div style="font-size:13px;">
            <div style="font-weight:600;">${fullName}</div>
            <div class="text-dim" style="font-size:11.5px;">Signed in</div>
          </div>
        </div>
        <button class="btn btn-outline btn-block" onclick="logout()">Log Out</button>
      </div>
    </aside>`;

  const toggle = document.getElementById("menu-toggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      document.getElementById("sidebar").classList.toggle("open");
    });
  }
}
