# API Specification — EV Charging Network

Base URL (local Docker): `http://localhost:8000/api`

All endpoints return JSON. Protected endpoints require an
`Authorization: Bearer <token>` header, where `<token>` is the JWT returned from `/register` or `/login`.
returned from `/register` or `/login`.

---

## Authentication

### `POST /api/register`
Create a new driver account.

**Body**
```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "0812345678",
  "password": "secret123",
  "confirm_password": "secret123"
}
```
**Response `201`**
```json
{ "access_token": "...", "token_type": "bearer", "user_id": 1, "full_name": "Jane Doe" }
```
Returns `400` if passwords don't match or the email is already registered.

### `POST /api/login`
Authenticate an existing driver.

**Body**
```json
{ "email": "jane@example.com", "password": "secret123", "remember_me": false }
```
**Response `200`**: same shape as `/register`. Returns `401` on bad credentials.

---

## Profile & Vehicles (protected)

### `GET /api/profile`
Returns the current driver's profile (name, email, wallet balance, reward points, settings).

### `PUT /api/profile`
Partially update the profile. Any subset of:
```json
{ "full_name": "...", "phone": "...", "avatar_url": "...", "dark_mode": true, "notifications_enabled": true }
```

### `GET /api/vehicles`
Lists the driver's saved vehicles.

### `POST /api/vehicles`
Add a vehicle.
```json
{ "make": "Tesla", "model": "Model 3", "year": 2023, "battery_capacity_kwh": 75, "connector_type": "CCS2", "license_plate": "กท-1234" }
```

### `GET /api/favorites` / `POST /api/favorites/{station_id}`
List or add a favorite station.

---

## Stations (protected)

### `GET /api/stations`
Query params: `search` (name filter), `fast_charge_only` (bool).
Returns a list of stations with pricing, rating, and open status.

### `GET /api/stations/{station_id}`
Returns full station detail including its list of chargers.
Returns `404` if the station doesn't exist.

---

## Bookings (protected)

### `POST /api/bookings`
Reserve a charging slot.
```json
{ "station_id": 1, "charger_id": 3, "vehicle_id": 2, "reservation_date": "2026-07-20", "reservation_time": "14:00" }
```
Validates the charger belongs to the station and is currently available
(`400`/`404` otherwise), then marks it unavailable and returns the created
booking with its estimated cost.

### `GET /api/bookings`
Lists the driver's bookings, most recent first.

### `GET /api/bookings/{booking_id}`
Returns a single booking owned by the driver. `404` if not found or not owned.

---

## Charging (protected)

### `POST /api/charging/start/{booking_id}`
Starts (or returns the existing) charging session tied to a booking.

### `GET /api/charging/status`
Returns the driver's most recent charging session. Each poll simulates
progress: battery percentage, remaining time, and running cost update
until the session reaches 100% or is stopped. `404` if no session exists.

### `POST /api/charging/stop`
Stops the active session, frees the charger, and marks the booking completed.

---

## Payments (protected)

### `POST /api/payments`
Pay for a session.
```json
{ "booking_id": 5, "amount": 320.5, "method": "credit_card" }
```
`method` is one of `credit_card`, `promptpay`, `wallet`. Wallet payments are
rejected with `400` if the balance is insufficient. Every payment awards
1 reward point per ฿10 spent.

### `GET /api/payments`
Lists the driver's payment history, most recent first.

---

## Error format

All errors follow FastAPI's default shape:
```json
{ "detail": "Human readable message" }
```

## Interactive docs

FastAPI auto-generates Swagger UI and ReDoc for this API:
- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`
