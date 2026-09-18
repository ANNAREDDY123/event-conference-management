 Event & Conference Management System

A FastAPI-based backend application for managing events and conferences, including event creation, venues, halls, speakers, sessions, attendee registration, ticketing, payments, session bookings, check-in, certificates, feedback, notifications, dashboards, reports, cancellations, refunds, security, and database management.

---

## 📌 Project Overview

The **Event & Conference Management System** is a backend REST API developed using **FastAPI** and **SQLAlchemy**.

The system provides APIs for managing the complete event lifecycle:

```text
User Registration & Login
        ↓
Create Event
        ↓
Add Venue & Hall
        ↓
Add Speaker
        ↓
Create Sessions
        ↓
Open Registration
        ↓
Register Attendee
        ↓
Create & Purchase Ticket
        ↓
Payment Processing
        ↓
Book Session
        ↓
Check-In
        ↓
Attend Event
        ↓
Submit Feedback
        ↓
Generate Certificate
        ↓
Reports & Dashboard
        ↓
Cancellation / Refund

The project follows a layered architecture:

Routes
   ↓
Services
   ↓
Repositories
   ↓
Models
   ↓
Database
🚀 Features
Level 1 — Authentication & Authorization
User registration
User login
JWT access tokens
JWT refresh tokens
Password hashing
Active/inactive user validation
Role-based authorization
Protected API endpoints
Supported Roles
Admin
Event Organizer
Speaker
Staff
Attendee
Level 2 — Event Management
Create events
View events
View event by ID
Update events
Delete events
Event types
Event statuses
Event date validation
Registration period validation
Event capacity validation
Event organizer ownership
Event search
Event filtering
Event sorting
Pagination
Available-capacity filtering
Event Types
Conference
Workshop
Seminar
Meetup
Training
Event Statuses
Draft
Published
Registration Open
Registration Closed
Completed
Cancelled
Level 3 — Venue & Hall Management
Create venues
View venues
View venue by ID
Update venues
Delete venues
Create halls
View halls by venue
View individual halls
Update halls
Delete halls
City filtering
Venue search
Venue sorting
Pagination
Venue capacity validation
Hall capacity validation
Level 4 — Speaker Management
Create speakers
View speakers
View speaker by ID
Update speakers
Delete speakers
Search speakers
Unique speaker email validation
Speaker expertise information
Speaker company information
Speaker experience
Active/inactive speaker status
Level 5 — Session Management
Create sessions
View sessions
View sessions by event
View session by ID
Update sessions
Delete sessions
Session types
Session statuses
Speaker assignment
Hall assignment
Session capacity validation
Event/session time validation
Hall conflict detection
Speaker conflict detection
Session Types
Keynote
Workshop
Panel
Technical
Networking
General
Session Statuses
Scheduled
Ongoing
Completed
Cancelled
Level 6 — Attendee Registration
Register attendees
View attendees
View attendees by event
View attendee by ID
Update attendee status
Cancel attendee registration
Validate event capacity
Prevent duplicate registration
Registration notifications
Level 7 — Ticket Management
Create tickets
View tickets
View tickets by event
View ticket by ID
Update tickets
Delete tickets
Ticket quantity management
Available ticket quantity tracking
Sold-out status
Ticket type management
Event capacity validation
Ticket Types
Regular
VIP
Early Bird
Ticket Statuses
Available
Sold Out
Inactive
Level 8 — Ticket Purchase & Payment
Purchase tickets
View purchases
View purchases by attendee
View purchases by ticket
Payment status management
Payment success/failure handling
Payment reference generation
Ticket availability updates
Sold-out handling
Ticket purchase cancellation
Ticket refund processing
Refund notifications
Payment Statuses
Pending
Success
Failed
Refunded
Level 9 — Session Booking
Book sessions
View bookings
View bookings by attendee
View bookings by session
Cancel session bookings
Update bookings
Delete bookings
Prevent duplicate bookings
Session capacity validation
Event ownership validation
Cancelled session protection
Completed session protection
Session booking notifications
Level 10 — Check-In
Attendee check-in
View check-in records
View check-in by attendee
View check-in by event
Update check-in status
Delete check-in
Prevent duplicate check-in
Event/attendee validation
Level 11 — Certificates
Generate event certificates
View certificates
View certificate by ID
View certificates by attendee
View certificates by event
Certificate number generation
Unique certificate numbers
Completed-event validation
Prevent duplicate certificates

Certificate format:

CERT-E{event_id}-{number}
Level 12 — Feedback & Ratings
Submit event feedback
View feedback
View feedback by attendee
View feedback by event
Update feedback
Delete feedback
Rating validation
Comment validation
Prevent duplicate feedback
Completed-event validation
Rating

Ratings are supported from:

1 to 5
Level 13 — Notifications

The system automatically generates notifications for important events.

Supported notification types include:

Registration
Ticket Purchase
Payment
Session Booking
Event Cancellation
Refund
Certificate
General

Notification features:

Create notification
View notifications
Filter unread/read notifications
Mark notification as read
Delete notification
User ownership validation
Level 14 — Search, Filtering, Pagination & Sorting

The project supports:

Event search
Event filtering
Event type filtering
Event status filtering
Date filtering
Available-capacity filtering
Event sorting
Event pagination
Venue search
Venue city filtering
Venue status filtering
Venue sorting
Venue pagination

Pagination uses:

page
page_size

Sorting supports:

sort_by
sort_order
Level 15 — Dashboard & Reports
Admin Dashboard

Provides:

Total events
Active events
Completed events
Total attendees
Total registrations
Total tickets sold
Total revenue
Total refunds
Average event rating
Organizer Dashboard

Provides:

Event registrations
Ticket sales
Revenue
Attendance
Session bookings
Speaker performance
Session popularity
Reports
Daily registrations
Event revenue
Ticket sales
Attendance
Speaker ratings
Session popularity
Level 16 — Cancellation & Refund Management

The system supports:

Event cancellation
Attendee cancellation
Ticket purchase refunds
Automatic ticket quantity restoration
Automatic refund processing for successful purchases
Event cancellation notifications
Refund notifications
Session booking cancellation
Level 17 — Security & Data Integrity

Security features include:

JWT authentication
Access token validation
Refresh token validation
Password hashing
Active user validation
Role-based authorization
Resource ownership validation
Protected state changes
Duplicate record prevention
Unique database constraints
Foreign key relationships
Input validation
Capacity validation
Level 18 — Clean Architecture

The application follows a layered architecture:

┌─────────────────────────┐
│        Routes           │
│   HTTP/API endpoints    │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│       Services          │
│    Business logic       │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│      Repositories       │
│     Database access     │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│         Models          │
│    SQLAlchemy ORM       │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│        Database         │
│ SQLite / SQLAlchemy     │
└─────────────────────────┘

Responsibilities:

Routes

Handle:

HTTP requests
Authentication dependencies
Request/response schemas
Calling service methods
Services

Handle:

Business rules
Validation
Authorization logic
Workflow processing
Repositories

Handle:

Database queries
Database inserts
Updates
Deletes
Aggregations
Database-related operations
Models

Define:

Database tables
Relationships
Constraints
Indexes
Level 19 — Database & Performance

Database/performance work includes:

SQLAlchemy database configuration
SQLite support
Database session management
Foreign-key indexes
Frequently filtered-column indexes
Unique indexes
Search/filter indexes
Date/time indexes
Status indexes
Repository-based database access
Aggregation queries for dashboards and reports
Pagination
Query filtering before pagination
Database-level counting and aggregation

The database contains indexes on important fields such as:

events.organizer_id
events.event_type
events.status
events.start_date

attendees.user_id
attendees.event_id
attendees.status

sessions.event_id
sessions.speaker_id
sessions.hall_id
sessions.start_time
sessions.end_time
sessions.status

session_bookings.attendee_id
session_bookings.session_id
session_bookings.status

ticket_purchases.ticket_id
ticket_purchases.attendee_id
ticket_purchases.payment_status
ticket_purchases.purchase_status

notifications.user_id
notifications.status
notifications.created_at

venues.city
venues.status
🛠️ Technology Stack
Technology	Purpose
Python 3.10+	Programming language
FastAPI	REST API framework
SQLAlchemy	ORM / database access
Pydantic	Data validation
Pydantic Settings	Configuration management
SQLite	Development database
PyJWT	JWT authentication
pwdlib	Password hashing
Argon2	Password hashing algorithm
Uvicorn	ASGI server
Pytest	Automated testing
HTTPX	API testing
📁 Project Structure
event-conference-management/
│
├── app/
│   │
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── create_tables.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── attendee.py
│   │   ├── certificate.py
│   │   ├── check_in.py
│   │   ├── event.py
│   │   ├── feedback.py
│   │   ├── notification.py
│   │   ├── session.py
│   │   ├── session_booking.py
│   │   ├── speaker.py
│   │   ├── ticket.py
│   │   ├── ticket_purchase.py
│   │   ├── user.py
│   │   └── venue.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── attendee_repository.py
│   │   ├── auth_repository.py
│   │   ├── certificate_repository.py
│   │   ├── check_in_repository.py
│   │   ├── dashboard_repository.py
│   │   ├── event_repository.py
│   │   ├── feedback_repository.py
│   │   ├── notification_repository.py
│   │   ├── session_booking_repository.py
│   │   ├── session_repository.py
│   │   ├── speaker_repository.py
│   │   ├── ticket_purchase_repository.py
│   │   ├── ticket_repository.py
│   │   └── venue_repository.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── attendees.py
│   │   ├── auth.py
│   │   ├── certificates.py
│   │   ├── check_ins.py
│   │   ├── dashboard.py
│   │   ├── events.py
│   │   ├── feedback.py
│   │   ├── notification.py
│   │   ├── session_bookings.py
│   │   ├── sessions.py
│   │   ├── speakers.py
│   │   ├── ticket_purchases.py
│   │   ├── tickets.py
│   │   └── venues.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── attendee.py
│   │   ├── auth.py
│   │   ├── certificate.py
│   │   ├── check_in.py
│   │   ├── dashboard.py
│   │   ├── event.py
│   │   ├── feedback.py
│   │   ├── notification.py
│   │   ├── session.py
│   │   ├── session_booking.py
│   │   ├── speaker.py
│   │   ├── ticket.py
│   │   ├── ticket_purchase.py
│   │   └── venue.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── attendee_service.py
│   │   ├── auth_service.py
│   │   ├── certificate_service.py
│   │   ├── check_in_service.py
│   │   ├── dashboard_service.py
│   │   ├── event_service.py
│   │   ├── feedback_service.py
│   │   ├── notification_service.py
│   │   ├── session_booking_service.py
│   │   ├── session_service.py
│   │   ├── speaker_service.py
│   │   ├── ticket_purchase_service.py
│   │   ├── ticket_service.py
│   │   └── venue_service.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_attendees.py
│   │   ├── test_auth.py
│   │   ├── test_certificate.py
│   │   ├── test_check_in.py
│   │   ├── test_dashboard.py
│   │   ├── test_events.py
│   │   ├── test_feedback.py
│   │   ├── test_level16_cancellation_refunds.py
│   │   ├── test_level17_security.py
│   │   ├── test_notifications.py
│   │   ├── test_session_bookings.py
│   │   ├── test_sessions.py
│   │   ├── test_speakers.py
│   │   ├── test_ticket_purchases.py
│   │   ├── test_tickets.py
│   │   └── test_venues.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── dependencies.py
│       └── security.py
│
├── .gitignore
├── README.md
└── requirements.txt
⚙️ Installation & Setup
1. Clone the repository
git clone https://github.com/ANNAREDDY123/event-conference-management.git

Move into the project directory:

cd event-conference-management
2. Create a virtual environment
Windows
python -m venv venv

Activate it:

venv\Scripts\Activate.ps1
Linux / macOS
python3 -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
🔐 Environment Configuration

The application supports configuration through environment variables.

Create a .env file in the project root if required:

DATABASE_URL=sqlite:///./event_conference.db
SECRET_KEY=change-this-secret-key-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

Do not commit the .env file to GitHub.

The project includes .gitignore rules to prevent sensitive environment files from being committed.

🗄️ Database

The default development database is:

SQLite

Default database URL:

sqlite:///./event_conference.db

The database tables can be created using:

python app/create_tables.py
▶️ Running the Application

Start the FastAPI server using:

uvicorn app.main:app --reload

The application will normally be available at:

http://127.0.0.1:8000
📚 API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI

Open:

http://127.0.0.1:8000/docs

Swagger UI can be used to:

View API endpoints
View request schemas
View response schemas
Authorize using JWT
Execute API requests
Test API responses
ReDoc

Open:

http://127.0.0.1:8000/redoc
🔑 Authentication

Most protected endpoints require a JWT access token.

1. Register

Example:

POST /auth/register

Request:

{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "TestPassword123",
  "role": "Attendee"
}
2. Login

Example:

POST /auth/login

Request:

{
  "email": "john@example.com",
  "password": "TestPassword123"
}

The login response provides an access token.

3. Authorize Swagger

In Swagger UI:

Open /docs
Click Authorize
Enter the required Bearer token
Click Authorize
Test protected endpoints

The authentication format is:

Bearer <access_token>
👥 Role-Based Access

The application supports role-based access control.

Admin
Event Organizer
Speaker
Staff
Attendee

Protected operations verify the authenticated user's role and, where required, ownership of the resource.

🧪 Testing

The project uses Pytest for automated testing.

Run the complete test suite:

pytest -q

Current verified result:

187 passed, 931 warnings

The test suite covers:

Authentication
Authorization
Events
Venues
Halls
Speakers
Sessions
Attendees
Tickets
Ticket purchases
Payments
Session bookings
Check-in
Certificates
Feedback
Notifications
Dashboard
Cancellation/refunds
Security
🔄 Complete Event Workflow

The main business workflow is:

1. Register User
       ↓
2. Login
       ↓
3. Create Event
       ↓
4. Add Venue
       ↓
5. Add Hall
       ↓
6. Add Speaker
       ↓
7. Create Session
       ↓
8. Open Event Registration
       ↓
9. Register Attendee
       ↓
10. Create Ticket
       ↓
11. Purchase Ticket
       ↓
12. Process Payment
       ↓
13. Book Session
       ↓
14. Check-In
       ↓
15. Attend Event
       ↓
16. Submit Feedback
       ↓
17. Generate Certificate
       ↓
18. View Dashboard / Reports
📊 Dashboard APIs

The application provides dashboard and reporting APIs including:

GET /dashboard/admin
GET /dashboard/organizer
GET /dashboard/organizer/{event_id}/speaker-performance
GET /dashboard/organizer/{event_id}/session-popularity
GET /dashboard/reports/daily-registrations
GET /dashboard/reports/event-revenue
GET /dashboard/reports/ticket-sales
GET /dashboard/reports/attendance
GET /dashboard/reports/speaker-ratings
GET /dashboard/reports/session-popularity
🔁 Cancellation & Refund APIs

The system supports cancellation and refund workflows.

Examples include:

PUT /ticket-purchases/{purchase_id}/refund

Event cancellation can automatically process eligible ticket refunds and notifications.

🛡️ Security

Security measures implemented in the project include:

JWT authentication
Password hashing
Role-based access control
Active-user validation
Protected endpoints
Ownership checks
Input validation
Unique constraints
Foreign-key relationships
Capacity validation
Duplicate-operation protection
Controlled state transitions
🧱 Architecture

The project uses a layered architecture to separate responsibilities.

Client
  │
  ▼
FastAPI Routes
  │
  ▼
Service Layer
  │
  ▼
Repository Layer
  │
  ▼
SQLAlchemy Models
  │
  ▼
SQLite Database

This structure improves:

Maintainability
Testability
Separation of concerns
Code organization
Reusability
🧪 Test Command Summary

Run all tests:

pytest -q

Run a specific test file:

pytest app/tests/test_events.py -q

Run authentication tests:

pytest app/tests/test_auth.py -q
🌐 API Server Commands

Start normally:

uvicorn app.main:app

Start with automatic reload during development:

uvicorn app.main:app --reload
📌 Project Status
Level 1  - Authentication & Authorization      ✅
Level 2  - Event Management                    ✅
Level 3  - Venue & Hall Management             ✅
Level 4  - Speaker Management                  ✅
Level 5  - Session Management                  ✅
Level 6  - Attendee Registration                ✅
Level 7  - Ticket Management                   ✅
Level 8  - Ticket Purchase & Payment           ✅
Level 9  - Session Booking                     ✅
Level 10 - Check-In                            ✅
Level 11 - Certificates                        ✅
Level 12 - Feedback & Ratings                  ✅
Level 13 - Notifications                       ✅
Level 14 - Search/Filtering/Pagination         ✅
Level 15 - Dashboard & Reports                 ✅
Level 16 - Cancellation & Refunds               ✅
Level 17 - Security & Data Integrity           ✅
Level 18 - Clean Architecture                 ✅
Level 19 - Database & Performance             ✅
📈 Current Test Status
187 passed
931 warnings

The test suite has been used throughout development to verify that existing functionality continues to work after architectural and feature changes.

🔮 Future Enhancements

Potential future enhancements include:

QR-code based check-in
PDF certificate generation
Excel report export
Redis caching
WebSocket-based live updates
Docker containerization
Celery background jobs
API versioning
Advanced automated testing
Production database deployment
👨‍💻 Development

This project was developed as an advanced FastAPI backend assignment with a focus on:

REST API development
Backend architecture
Database management
Authentication
Authorization
Business logic
API testing
Database performance
Clean architecture

