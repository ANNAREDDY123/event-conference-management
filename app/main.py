from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.auth import router as auth_router
from app.routes.events import router as events_router
from app.routes.speakers import router as speakers_router
from app.routes.venues import router as venues_router
from app.routes.sessions import router as sessions_router
from app.routes.attendees import router as attendee_router
from app.routes.tickets import router as ticket_router
from app.routes.ticket_purchases import router as ticket_purchase_router
from app.routes.session_bookings import router as session_booking_router
from app.routes.check_ins import router as check_in_router
from app.routes.certificates import router as certificate_router
from app.routes.feedback import router as feedback_router
from app.routes.notification import router as notification_router
from app.routes.dashboard import router as dashboard_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Event & Conference Management System API",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(events_router)
app.include_router(venues_router)
app.include_router(speakers_router)
app.include_router(sessions_router)
app.include_router(attendee_router)
app.include_router(ticket_router)
app.include_router(ticket_purchase_router)
app.include_router(session_booking_router)
app.include_router(check_in_router)
app.include_router(certificate_router)
app.include_router(feedback_router)
app.include_router(notification_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {
        "message": "Event & Conference Management System API",
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }