"""
state.py – Application State / Controller
Holds all runtime data and seeds demo content.
"""

import random
from models import (
    User, Vehicle, ParkingLot, ParkingSpot,
    Booking, Payment, Notification,
)


class AppState:
    def __init__(self):
        self.users:         dict[str, User]    = {}
        self.vehicles:      list[Vehicle]      = []
        self.parking_lots:  list[ParkingLot]   = []
        self.bookings:      list[Booking]      = []
        self.payments:      list[Payment]      = []
        self.notifications: list[Notification] = []
        self.current_user:  User | None        = None
        self._seed_data()

    # ── helpers ──────────────────────────────────────────────────────────

    def register_user(self, first_name, username, email, password, phone="") -> User:
        u = User(first_name, username, email, password, phone)
        self.users[username] = u
        return u

    def add_vehicle(self, license_plate, vehicle_type="sedan", model="") -> Vehicle:
        assert self.current_user, "No user logged in"
        v = Vehicle(license_plate, self.current_user.userID, vehicle_type, model)
        self.vehicles.append(v)
        return v

    def remove_vehicle(self, vehicle_id: int):
        self.vehicles = [v for v in self.vehicles if v.vehicleID != vehicle_id]

    def make_booking(self, lot: ParkingLot, hours: int,
                     extra_services: list[str]) -> tuple[Booking, Payment] | None:
        """Reserve first available spot, create booking + payment. Returns (Booking, Payment) or None."""
        assert self.current_user
        spots = lot.getAvailableSpots()
        if not spots:
            return None

        spot    = spots[0]
        booking = Booking(self.current_user.userID, spot.spotID,
                          vehicle_id=1, hours=hours)
        booking.createBooking()
        self.bookings.append(booking)

        payment = Payment(booking.bookingID, hours, extra_services=extra_services)
        payment.processPayment()
        self.payments.append(payment)

        spot.isBooked = True
        spot.status   = "occupied"
        spot.sensor.detectEntry(spot)

        notif = Notification(
            self.current_user.userID,
            f"Spot {spot.spotID} booked at {lot.name}",
            "booking",
        )
        self.notifications.append(notif)
        return booking, payment

    def cancel_booking(self, booking: Booking):
        booking.cancelBooking()
        for lot in self.parking_lots:
            for sp in lot.spots:
                if sp.spotID == booking.spotID:
                    sp.isBooked = False
                    sp.status   = "available"
        notif = Notification(
            self.current_user.userID,
            f"Booking #{booking.bookingID} cancelled",
            "cancel",
        )
        self.notifications.append(notif)

    def my_bookings(self) -> list[Booking]:
        if not self.current_user:
            return []
        return [b for b in self.bookings if b.userID == self.current_user.userID]

    def my_vehicles(self) -> list[Vehicle]:
        if not self.current_user:
            return []
        return [v for v in self.vehicles if v.ownerID == self.current_user.userID]

    def my_notifications(self) -> list[Notification]:
        if not self.current_user:
            return []
        return [n for n in self.notifications if n.userID == self.current_user.userID]

    def payment_for(self, booking_id: int) -> Payment | None:
        return next((p for p in self.payments if p.bookingID == booking_id), None)

    # ── seed ─────────────────────────────────────────────────────────────

    def _seed_data(self):
        lots = [
            ParkingLot("King Fahad Parking",        20, "25.1972,55.2744", "King Fahad Parking, Business Bay"),
            ParkingLot("Mall of ALnakeel",  50, "25.1181,55.2003", "Mall of ALnakeel, Business Bay"),
        ]
        for lot in lots:
            for i in range(lot.totalSpots):
                sp = ParkingSpot(
                    f"Level {i // 5 + 1} – {chr(65 + i % 5)}{i % 5 + 1}",
                    lot.lotID,
                )
                if random.random() < 0.4:
                    sp.isBooked = True
                    sp.status   = "occupied"
                lot.spots.append(sp)
            self.parking_lots.append(lot)


# Singleton used by every UI module
STATE = AppState()
