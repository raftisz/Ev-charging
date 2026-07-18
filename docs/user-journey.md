# User Journey — EV Charging Network

This document walks through the primary flows a driver takes through the
Volt Grid application, from signing up to completing a charging session.

## 1. Onboarding

1. A new driver lands on `login.html` and selects **Register**.
2. They fill in full name, email, phone, and password on `register.html`.
3. On success, the backend returns a JWT which is stored in `localStorage`,
   and the driver is redirected straight into `dashboard.html`.

## 2. Returning driver

1. The driver opens the app; `index.html` checks for a stored JWT.
2. If a token exists, they are sent directly to the dashboard.
3. If not, they land on `login.html`, enter their credentials, and
   optionally check **Remember Me** for a longer-lived session.

## 3. Finding a station

1. From the dashboard, the driver selects **+ New Reservation** or
   **Find Stations** in the sidebar.
2. `stations.html` lists nearby stations as cards with distance, price,
   rating, and open status.
3. The driver searches by name, filters to fast-charge-only stations, or
   sorts by price/rating.
4. Selecting a card opens `station-detail.html`, showing chargers,
   amenities, reviews, and a map placeholder.

## 4. Reserving a slot

1. From the station detail page, the driver selects **Reserve This
   Station**, landing on `reservation.html` with the station pre-filled.
2. They pick a date, time, available charger, and (optionally) a vehicle
   from their profile.
3. The estimated cost updates live in the summary panel.
4. Confirming the reservation creates a `Booking` record and marks the
   chosen charger as unavailable.

## 5. Charging

1. After confirming, the driver is routed to `charging-status.html`.
2. The page polls `GET /api/charging/status` every few seconds, animating
   the signature charge ring as the battery percentage climbs.
3. The driver can select **Stop Charging** at any time, which finalizes the
   session and frees the charger.

## 6. Paying

1. Once a session ends, `payment.html` shows the final cost.
2. The driver chooses Credit Card, PromptPay QR, or their Volt Grid Wallet
   balance, then confirms payment.
3. A successful payment awards reward points and appears in the driver's
   payment history.

## 7. Reviewing history & profile

1. `history.html` offers three tabs: Reservations, Charging, and Payments,
   each pulling from the corresponding API endpoints.
2. `profile.html` lets the driver update personal details, manage saved
   vehicles, and toggle dark mode / notification preferences.

## Journey Summary Diagram

```
Register/Login → Dashboard → Find Stations → Station Detail
      → Reservation → Charging Status → Payment → History
```
