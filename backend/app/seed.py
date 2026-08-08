"""Database seeding helpers for the EV Charging Network demo data."""

import random
from datetime import datetime, timedelta

from sqlmodel import Session, select

from app import crud, models
from app.database import engine

STATION_NAMES = [
    "Sukhumvit Supercharge Hub",
    "Siam Green Station",
    "Riverside EV Point",
    "Central Park Charging Bay",
    "Northline Fast Charge",
    "Sathorn Business Hub",
    "Chatuchak Charge & Go",
    "Rama IX Power Station",
    "Ekkamai Urban Charger",
    "Bang Na Highway Stop",
    "Ratchada Night Charge",
    "Ari Neighborhood Station",
    "Thonglor Premium Charge",
    "Phrom Phong Skyline Hub",
    "Ladprao Community Charger",
    "Silom District Point",
    "Asoke Intersection Hub",
    "Bangna Trad Express",
    "Onnut Local Charger",
    "Suvarnabhumi Airport Hub",
]


def seed_mock_data() -> None:
    """Insert demo stations, users, vehicles, bookings, sessions, and payments."""
    with Session(engine) as session:
        if session.exec(select(models.Station)).first():
            return

        stations_list = []
        for i, name in enumerate(STATION_NAMES):
            station = models.Station(
                name=name,
                address=f"{100 + i} Charging Road, Bangkok",
                city="Bangkok",
                latitude=13.7563 + random.uniform(-0.08, 0.08),
                longitude=100.5018 + random.uniform(-0.08, 0.08),
                image_url=f"https://picsum.photos/seed/evstation{i}/600/400",
                description=(
                    "A modern EV charging hub with fast and standard chargers, "
                    "a waiting lounge, and nearby amenities."
                ),
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

        demo_users = []
        for i in range(10):
            user = models.User(
                full_name="Admin User" if i == 0 else f"Demo User {i}",
                email="admin@example.com" if i == 0 else f"user{i}@example.com",
                phone=f"08{random.randint(10000000, 99999999)}",
                password_hash=crud.hash_password("password123"),
                wallet_balance=round(random.uniform(200, 2000), 2),
                reward_points=random.randint(0, 500),
                avatar_url=f"https://i.pravatar.cc/150?u=user{i}",
                role="admin" if i == 0 else "user",
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

        station = stations_list[0]
        chargers = session.exec(select(models.Charger).where(models.Charger.station_id == station.id)).all()

        bookings = []
        for i in range(30):
            user = random.choice(demo_users[1:])
            charger = random.choice(chargers)
            booked_at = datetime.utcnow() - timedelta(days=random.randint(1, 45))
            status = "completed" if i < 20 else random.choice(["cancelled", "confirmed"])
            booking = models.Booking(
                user_id=user.id,
                station_id=station.id,
                charger_id=charger.id,
                vehicle_id=session.exec(select(models.Vehicle).where(models.Vehicle.user_id == user.id)).first().id,
                reservation_date=(booked_at - timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d"),
                reservation_time=f"{random.randint(8, 20)}:00",
                estimated_cost=round(station.price_per_kwh * random.uniform(20, 50), 2),
                status=status,
                created_at=booked_at,
            )
            session.add(booking)
            bookings.append(booking)
        session.commit()

        charging_sessions = []
        for booking in bookings[:20]:
            session.refresh(booking)
            charging_session = models.ChargingSession(
                booking_id=booking.id,
                user_id=booking.user_id,
                battery_percent=100,
                charging_progress=100,
                power_output_kw=random.choice([22.0, 60.0, 120.0]),
                charging_speed="Fast",
                remaining_minutes=0,
                current_cost=booking.estimated_cost,
                status="completed",
                started_at=booking.created_at,
                ended_at=booking.created_at + timedelta(minutes=random.randint(30, 80)),
            )
            session.add(charging_session)
            charging_sessions.append(charging_session)
        session.commit()

        for booking in bookings:
            session.refresh(booking)
            payment = models.Payment(
                user_id=booking.user_id,
                booking_id=booking.id,
                amount=booking.estimated_cost,
                method=random.choice(["credit_card", "promptpay", "wallet"]),
                status="paid",
                created_at=booking.created_at + timedelta(minutes=5),
            )
            session.add(payment)
        session.commit()

        session.add(models.Favorite(user_id=demo_users[1].id, station_id=station.id))
        session.commit()
