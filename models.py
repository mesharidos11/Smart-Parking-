"""
models.py – Data Models (from UML Class Diagram)
"""

import datetime
import random


class User:
    _next_id = 1

    def __init__(self, first_name, username, email, password, phone=""):
        self.userID    = User._next_id
        User._next_id += 1
        self.name      = first_name
        self.username  = username
        self.email     = email
        self._password = password
        self.phone     = phone

    def register(self):
        return True

    def login(self, password):
        return self._password == password

    def __str__(self):
        return f"{self.name} ({self.username})"


class Vehicle:
    _next_id = 1
    TYPES = {"sedan": "🚗", "suv": "🚙", "truck": "🚛", "ev": "⚡"}

    def __init__(self, license_plate, owner_id, vehicle_type="sedan", model=""):
        self.vehicleID    = Vehicle._next_id
        Vehicle._next_id += 1
        self.licensePlate = license_plate
        self.ownerID      = owner_id
        self.vehicle_type = vehicle_type
        self.model        = model

    def addVehicle(self):
        return True

    def __str__(self):
        return f"{self.model} – {self.licensePlate}"


class SensorSystem:
    _next_id = 1

    def __init__(self, spot_id):
        self.sensorID    = SensorSystem._next_id
        SensorSystem._next_id += 1
        self.spotID      = spot_id
        self.lastUpdated = datetime.datetime.now()

    def detectEntry(self, spot: "ParkingSpot"):
        spot.isBooked    = True
        spot.status      = "occupied"
        self.lastUpdated = datetime.datetime.now()

    def detectExit(self, spot: "ParkingSpot"):
        spot.isBooked    = False
        spot.status      = "available"
        self.lastUpdated = datetime.datetime.now()

    def updateSpotStatus(self, spot: "ParkingSpot", status: str):
        spot.status = status


class ParkingSpot:
    _next_id = 1

    def __init__(self, location, lot_id):
        self.spotID   = ParkingSpot._next_id
        ParkingSpot._next_id += 1
        self.location = location
        self.status   = "available"
        self.isBooked = False
        self.lotID    = lot_id
        self.sensor   = SensorSystem(self.spotID)

    def updateStatus(self, status):
        self.status = status

    def getStatus(self):
        return self.status

    def __str__(self):
        return f"Spot #{self.spotID} – {self.location}"


class ParkingLot:
    _next_id = 1

    def __init__(self, name, total_spots, coordinates, address=""):
        self.lotID       = ParkingLot._next_id
        ParkingLot._next_id += 1
        self.name        = name
        self.totalSpots  = total_spots
        self.coordinates = coordinates
        self.address     = address
        self.spots: list[ParkingSpot] = []

    def getAvailableSpots(self):
        return [s for s in self.spots if not s.isBooked]

    def displayMap(self):
        return f"Map: {self.name} @ {self.coordinates}"


class Booking:
    _next_id = 1

    def __init__(self, user_id, spot_id, vehicle_id, hours=1):
        self.bookingID = Booking._next_id
        Booking._next_id += 1
        self.startTime = datetime.datetime.now()
        self.endTime   = self.startTime + datetime.timedelta(hours=hours)
        self.status    = "active"
        self.spotID    = spot_id
        self.userID    = user_id
        self.vehicleID = vehicle_id

    def createBooking(self):
        self.status = "active"
        return True

    def cancelBooking(self):
        self.status = "cancelled"
        return True

    def getDuration(self):
        delta = self.endTime - self.startTime
        return round(delta.total_seconds() / 3600, 1)

    def __str__(self):
        return f"Booking #{self.bookingID} | Spot {self.spotID} | {self.status}"


class Payment:
    _next_id = 1
    RATES = {1: 20, 2: 35, 3: 60, 4: 80}   # hours → SAR

    def __init__(self, booking_id, hours=1, method="card", extra_services=None):
        self.paymentID = Payment._next_id
        Payment._next_id += 1
        self.bookingID = booking_id
        self.amount    = self.calculateFee(hours, extra_services or [])
        self.method    = method
        self.status    = "pending"

    def calculateFee(self, hours, extra_services):
        base   = self.RATES.get(hours, hours * 20)
        extras = {"electric_charge": 40, "car_wash": 30}
        return base + sum(extras.get(s, 0) for s in extra_services)

    def processPayment(self):
        self.status = "paid"
        return True

    def getReceipt(self):
        return (
            f"Receipt – Payment #{self.paymentID} "
            f"| {self.amount} SAR | {self.method}"
        )


class Notification:
    _next_id = 1

    def __init__(self, user_id, message, notif_type="info"):
        self.notifID = Notification._next_id
        Notification._next_id += 1
        self.userID  = user_id
        self.message = message
        self.type    = notif_type

    def sendAlert(self):
        return f"[ALERT] {self.message}"

    def notifyOvertime(self):
        return f"[OVERTIME] {self.message}"


class Navigation:
    _next_id = 1

    def __init__(self, user_id, target_spot, mode="driving"):
        self.navID      = Navigation._next_id
        Navigation._next_id += 1
        self.userID     = user_id
        self.targetSpot = target_spot
        self.mode       = mode

    def getVehicleRoute(self):
        return f"🚗 Route (driving) to spot {self.targetSpot}"

    def getPedestrianRoute(self):
        return f"🚶 Route (walking) to spot {self.targetSpot}"

    def startNavigation(self):
        return f"Navigation started → Spot {self.targetSpot}"
