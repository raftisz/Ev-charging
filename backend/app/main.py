"""
EV Charging Network - FastAPI application entrypoint.

Responsibilities:
- Create DB tables and seed mock data on startup.
- Register feature routers under /api.
- Serve the vanilla HTML/CSS/JS frontend as static files.
"""

import random
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from app import crud, models
from app.database import create_db_and_tables, engine
from app.routers import auth, bookings, charging, payments, stations, users

app = FastAPI(
    title="EV Charging Network API",
    description="Backend API for finding stations, reserving chargers, and managing EV charging sessions.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(stations.router)
app.include_router(bookings.router)
app.include_router(charging.router)
app.include_router(payments.router)


STATION_NAMES = [
    "Sukhumvit Supercharge Hub", "Siam Green Station", "Riverside EV Point", "Central Park Charging Bay",
    "Northline Fast Charge", "Sathorn Business Hub", "Chatuchak Charge & Go", "Rama IX Power Station",
    "Ekkamai Urban Charger", "Bang Na Highway Stop", "Ratchada Night Charge", "Ari Neighborhood Station",
    "Thonglor Premium Charge", "Phrom Phong Skyline Hub", "Ladprao Community Charger", "Silom District Point",
    "Asoke Intersection Hub", "Bangna Trad Express", "Onnut Local Charger", "Suvarnabhumi Airport Hub",
]


def seed_mock_data() -> None:
    """Insert demo stations, users, vehicles, and history if the DB is empty."""
    with Session(engine) as session:
        if session.exec(select(models.Station)).first():
            return  # already seeded

        # --- Stations & chargers ---
        stations_list = []
        for i, name in enumerate(STATION_NAMES):
            station = models.Station(
                name=name,
                address=f"{100 + i} Charging Road, Bangkok",
                city="Bangkok",
                latitude=13.7563 + random.uniform(-0.08, 0.08),
                longitude=100.5018 + random.uniform(-0.08, 0.08),
                image_url=f"https://picsum.photos/seed/evstation{i}/600/400",
                description="A modern EV charging hub with fast and standard chargers, "
                             "a waiting lounge, and nearby amenities.",
                rating=round(random.uniform(3.8, 5.0), 1),
                price_per_kwh=round(random.uniform(6.5, 11.5), 2),
                has_fast_charge=random.choice([True, True, False]),
                is_open=random.choice([True, True, True, False]),
                opening_hours=random.choice(["24 Hours", "06:00 - 24:00", "07:00 - 22:00"]),
                amenities=random.choice([
                    "Wi-Fi, Restroom, Cafe",
                    "Wi-Fi, Convenience Store",
                    "Restroom, Lounge, Vending Machine",
                    "Wi-Fi, Restroom, Cafe, Lounge",
                ]),
            )
            session.add(station)
            stations_list.append(station)
        session.commit()

        for station in stations_list:
            session.refresh(station)
            charger_count = random.randint(2, 5)
            for c in range(charger_count):
                charger = models.Charger(
                    station_id=station.id,
                    connector_type=random.choice(["CCS2", "Type 2", "CHAdeMO"]),
                    power_kw=random.choice([22.0, 60.0, 120.0, 180.0]),
                    is_available=random.choice([True, True, False]),
                    charger_code=f"{chr(65 + c)}{c + 1}",
                )
                session.add(charger)
        session.commit()

        # --- Users & vehicles ---
        demo_users = []
        for i in range(10):
            user = models.User(
                full_name=f"Demo User {i + 1}",
                email=f"user{i + 1}@example.com",
                phone=f"08{random.randint(10000000, 99999999)}",
                password_hash=crud.hash_password("password123"),
                wallet_balance=round(random.uniform(200, 2000), 2),
                reward_points=random.randint(0, 500),
                avatar_url=f"https://i.pravatar.cc/150?u=user{i + 1}",
            )
            session.add(user)
            demo_users.append(user)
        session.commit()

        for user in demo_users:
            session.refresh(user)
            vehicle = models.Vehicle(
                user_id=user.id,
                make=random.choice(["Tesla", "BYD", "MG", "ORA", "Hyundai"]),
                model=random.choice(["Model 3", "Atto 3", "MG4", "Good Cat", "Ioniq 5"]),
                year=random.randint(2021, 2025),
                battery_capacity_kwh=round(random.uniform(50, 100), 1),
                connector_type=random.choice(["CCS2", "Type 2"]),
                license_plate=f"กท-{random.randint(1000, 9999)}",
                is_default=True,
            )
            session.add(vehicle)
        session.commit()

        # --- Sample booking / charging / payment history for user1 ---
        primary_user = demo_users[0]
        session.refresh(primary_user)
        sample_station = stations_list[0]
        sample_chargers = session.exec(
            select(models.Charger).where(models.Charger.station_id == sample_station.id)
        ).all()

        for i in range(5):
            days_ago = (i + 1) * 3
            booking = models.Booking(
                user_id=primary_user.id,
                station_id=sample_station.id,
                charger_id=sample_chargers[0].id if sample_chargers else 1,
                reservation_date=(datetime.utcnow() - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
                reservation_time="14:00",
                estimated_cost=round(random.uniform(150, 500), 2),
                status="completed",
                created_at=datetime.utcnow() - timedelta(days=days_ago),
            )
            session.add(booking)
            session.commit()
            session.refresh(booking)

            charging_session = models.ChargingSession(
                booking_id=booking.id,
                user_id=primary_user.id,
                battery_percent=100,
                charging_progress=100,
                power_output_kw=60.0,
                charging_speed="Fast",
                remaining_minutes=0,
                current_cost=booking.estimated_cost,
                status="completed",
                started_at=booking.created_at,
                ended_at=booking.created_at + timedelta(minutes=40),
            )
            session.add(charging_session)

            payment = models.Payment(
                user_id=primary_user.id,
                booking_id=booking.id,
                amount=booking.estimated_cost,
                method=random.choice(["credit_card", "promptpay", "wallet"]),
                status="paid",
                created_at=booking.created_at + timedelta(minutes=41),
            )
            session.add(payment)
        session.commit()

        favorite = models.Favorite(user_id=primary_user.id, station_id=sample_station.id)
        session.add(favorite)
        session.commit()


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()
    seed_mock_data()


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": "EV Charging Network API"}


# Serve the vanilla HTML/CSS/JS frontend. Mounted last so it doesn't
# shadow the /api routes above.
app.mount("/", StaticFiles(directory="/app/frontend", html=True), name="frontend")
