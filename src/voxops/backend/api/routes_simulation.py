"""
VOXOPS AI Gateway — Simulation / Prediction Endpoints

GET /predict-delivery/{order_id}
  Returns an estimated delivery time for the given order.
  Uses route distance, vehicle speed, and traffic level for a basic estimate.
  Full SimPy integration will be added in Phase 5.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from configs.logging_config import get_logger
from src.voxops.database.db import get_db
from src.voxops.database.models import Order, Route, Vehicle

log = get_logger(__name__)

router = APIRouter(prefix="/simulation", tags=["simulation"])


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------

class DeliveryPrediction(BaseModel):
    order_id: str
    origin: str
    destination: str
    distance_km: float
    vehicle_id: str | None
    vehicle_speed_kmh: float | None
    traffic_level: str | None
    traffic_multiplier: float | None
    estimated_hours: float | None
    estimated_minutes: float | None
    confidence: str
    note: str


# ---------------------------------------------------------------------------
# GET /predict-delivery/{order_id}
# ---------------------------------------------------------------------------

@router.get("/predict-delivery/{order_id}", response_model=DeliveryPrediction)
def predict_delivery(order_id: str, db: Session = Depends(get_db)):
    """
    Estimate delivery time for an order.

    Basic formula (will be replaced by SimPy simulation in Phase 5):
        travel_time = distance / (speed × traffic_multiplier)
    """
    # Fetch order
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found.")

    # Fetch vehicle (if assigned)
    vehicle = None
    speed: float | None = None
    if order.vehicle_id:
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == order.vehicle_id).first()
        if vehicle:
            speed = vehicle.speed

    # Find matching route
    route = (
        db.query(Route)
        .filter(Route.origin == order.origin, Route.destination == order.destination)
        .first()
    )

    traffic_level: str | None = None
    traffic_mult: float | None = None
    if route:
        traffic_level = route.average_traffic
        traffic_mult = route.traffic_multiplier

    # Compute estimate
    estimated_hours: float | None = None
    estimated_minutes: float | None = None
    confidence = "low"
    note = ""

    if speed and speed > 0:
        multiplier = traffic_mult if traffic_mult else 0.80  # default medium
        effective_speed = speed * multiplier
        estimated_hours = round(order.distance / effective_speed, 2)
        estimated_minutes = round(estimated_hours * 60, 1)
        confidence = "medium" if route else "low"
        note = "Basic estimate using distance / (speed × traffic). Phase 5 adds SimPy simulation."
    else:
        note = "No vehicle assigned or vehicle speed unavailable — cannot estimate."

    log.info(
        "Delivery prediction for {}: {:.1f}h (confidence={})",
        order_id,
        estimated_hours or 0,
        confidence,
    )

    return DeliveryPrediction(
        order_id=order.order_id,
        origin=order.origin,
        destination=order.destination,
        distance_km=order.distance,
        vehicle_id=order.vehicle_id,
        vehicle_speed_kmh=speed,
        traffic_level=traffic_level,
        traffic_multiplier=traffic_mult,
        estimated_hours=estimated_hours,
        estimated_minutes=estimated_minutes,
        confidence=confidence,
        note=note,
    )
