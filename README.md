# RideGo - Ride Hailing Platform Backend

A production-ready Django backend for a ride-hailing platform like Uber/Ola.

## Project Structure

```
project/
├── rideapp/          # Main Django project settings
├── authsystem/       # User authentication with OTP
├── drivers/          # Driver management
├── rides/            # Ride booking system
├── utils/            # Ola Maps integration
├── core/             # Core endpoints (health, info)
└── media/            # Uploaded files
```

## Quick Start

### 1. Install Dependencies

```bash
pip install django djangorestframework django-cors-headers channels daphne
```

### 2. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser

```bash
python manage.py createsuperuser
```

### 4. Run Server

```bash
python manage.py runserver
```

Server runs at `http://localhost:8000`

---

## API Documentation

### Health Check

#### `GET /api/health/`

Check if backend is running.

**Response:**
```json
{
  "status": "backend running",
  "service": "RideGo API",
  "version": "1.0.0"
}
```

---

### Authentication

#### `POST /api/auth/login/`

Send OTP to phone number.

**Request:**
```json
{
  "phone_number": "9876543210"
}
```

**Response:**
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "dev_mode": true,
  "otp": "123456",
  "hint": "Use OTP 123456 in dev mode"
}
```

**Note:** In development mode, OTP is always `123456`. Set `DEV_BYPASS_OTP=False` in settings for production.

---

#### `POST /api/auth/verify/`

Verify OTP and login.

**Request:**
```json
{
  "phone_number": "9876543210",
  "otp": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "OTP verified successfully",
  "user": {
    "id": 1,
    "phone_number": "9876543210",
    "name": "",
    "email": null,
    "is_driver": false,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "is_new_user": true
}
```

---

### Drivers

#### `POST /api/drivers/register/`

Register as a driver.

**Request (multipart/form-data):**
```
phone_number: 9876543210
name: John Doe
vehicle_type: sedan
vehicle_number: MH12AB1234
license_number: DL1234567890
aadhaar_number: 123456789012
pan_number: ABCDE1234F
```

**Response:**
```json
{
  "success": true,
  "message": "Driver registered successfully. Awaiting approval.",
  "driver": {
    "id": 1,
    "name": "John Doe",
    "vehicle_type": "sedan",
    "vehicle_number": "MH12AB1234",
    "is_approved": false,
    "is_online": false,
    "rating": 5.0,
    "total_rides": 0
  }
}
```

---

#### `POST /api/drivers/toggle-online/`

Toggle driver online/offline status.

**Request:**
```json
{
  "phone_number": "9876543210"
}
```

**Response:**
```json
{
  "success": true,
  "is_online": true,
  "message": "Driver is now online"
}
```

---

#### `POST /api/drivers/update-location/`

Update driver's current location.

**Request:**
```json
{
  "phone_number": "9876543210",
  "lat": 19.0760,
  "lng": 72.8777
}
```

**Response:**
```json
{
  "success": true,
  "message": "Location updated"
}
```

---

#### `GET /api/drivers/nearby/`

Get nearby drivers.

**Query Parameters:**
- `lat` (required): Latitude
- `lng` (required): Longitude
- `radius` (optional): Search radius in km (default: 10)
- `vehicle_type` (optional): Filter by vehicle type

**Example:** `/api/drivers/nearby/?lat=19.0760&lng=72.8777&vehicle_type=sedan`

**Response:**
```json
{
  "success": true,
  "drivers": [
    {
      "id": 1,
      "name": "John Doe",
      "vehicle_type": "sedan",
      "vehicle_number": "MH12AB1234",
      "rating": 4.8,
      "current_lat": 19.0750,
      "current_lng": 72.8780,
      "distance_km": 1.5
    }
  ],
  "count": 1
}
```

---

#### `POST /api/drivers/documents/`

Upload driver documents.

**Request (multipart/form-data):**
```
phone_number: 9876543210
profile_photo: [file]
license_photo: [file]
rc_photo: [file]
```

**Response:**
```json
{
  "success": true,
  "message": "Documents uploaded successfully"
}
```

---

### Rides

#### `POST /api/rides/request/`

Request a new ride.

**Request:**
```json
{
  "phone_number": "9876543210",
  "pickup_lat": 19.0760,
  "pickup_lng": 72.8777,
  "drop_lat": 19.0180,
  "drop_lng": 72.8500,
  "vehicle_type": "mini"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Ride requested successfully",
  "ride": {
    "id": 1,
    "status": "searching_driver",
    "pickup_lat": 19.0760,
    "pickup_lng": 72.8777,
    "drop_lat": 19.0180,
    "drop_lng": 72.8500,
    "distance_km": 5.2,
    "estimated_fare": 72,
    "otp": "456789"
  },
  "nearby_drivers": [
    {"id": 1, "name": "John Doe", "distance_km": 1.5}
  ]
}
```

---

#### `GET /api/rides/status/{ride_id}/`

Get ride status.

**Response:**
```json
{
  "success": true,
  "ride": {
    "id": 1,
    "status": "driver_assigned",
    "pickup_lat": 19.0760,
    "pickup_lng": 72.8777,
    "pickup_address": "Mumbai, Maharashtra",
    "drop_lat": 19.0180,
    "drop_lng": 72.8500,
    "drop_address": "Mumbai, Maharashtra",
    "driver_details": {
      "id": 1,
      "name": "John Doe",
      "phone_number": "9876543210",
      "vehicle_type": "sedan",
      "vehicle_number": "MH12AB1234",
      "rating": 4.8,
      "current_lat": 19.0750,
      "current_lng": 72.8780
    },
    "otp": "456789",
    "distance_km": 5.2,
    "estimated_fare": 72
  }
}
```

---

#### `POST /api/rides/accept/`

Driver accepts a ride.

**Request:**
```json
{
  "ride_id": 1,
  "phone_number": "9876543210"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Ride accepted successfully",
  "ride": {
    "id": 1,
    "status": "driver_assigned",
    "otp": "456789",
    "pickup_address": "Mumbai, Maharashtra",
    "drop_address": "Mumbai, Maharashtra",
    "pickup_lat": 19.0760,
    "pickup_lng": 72.8777
  }
}
```

---

#### `POST /api/rides/update-status/`

Driver updates ride status.

**Request:**
```json
{
  "ride_id": 1,
  "phone_number": "9876543210",
  "status": "ride_started"
}
```

**Valid statuses:**
- `driver_arriving` - Driver is on the way
- `ride_started` - Ride has started
- `ride_completed` - Ride completed
- `cancelled` - Ride cancelled

**Response:**
```json
{
  "success": true,
  "message": "Ride status updated to ride_started",
  "ride": {
    "id": 1,
    "status": "ride_started",
    "final_fare": 72
  }
}
```

---

#### `POST /api/rides/cancel/`

Passenger cancels a ride.

**Request:**
```json
{
  "ride_id": 1,
  "phone_number": "9876543210"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Ride cancelled successfully"
}
```

---

### Maps (Ola Maps Integration)

#### `GET /api/maps/geocode/`

Convert address to coordinates.

**Query Parameters:**
- `address` (required): Address to geocode

**Example:** `/api/maps/geocode/?address=Mumbai%20Central`

**Response:**
```json
{
  "success": true,
  "result": {
    "lat": 18.9712,
    "lng": 72.8194,
    "formatted_address": "Mumbai Central, Mumbai, Maharashtra"
  }
}
```

---

#### `GET /api/maps/reverse-geocode/`

Convert coordinates to address.

**Query Parameters:**
- `lat` (required): Latitude
- `lng` (required): Longitude

**Example:** `/api/maps/reverse-geocode/?lat=19.0760&lng=72.8777`

**Response:**
```json
{
  "success": true,
  "result": {
    "formatted_address": "Mumbai, Maharashtra, India",
    "place_id": "ChIJdd4hrwug2EcRmSrV3Vo6llI"
  }
}
```

---

#### `GET /api/maps/route/`

Get route between two points.

**Query Parameters:**
- `origin_lat` (required)
- `origin_lng` (required)
- `dest_lat` (required)
- `dest_lng` (required)

**Example:** `/api/maps/route/?origin_lat=19.0760&origin_lng=72.8777&dest_lat=19.0180&dest_lng=72.8500`

**Response:**
```json
{
  "success": true,
  "route": {
    "distance_km": 5.2,
    "duration_minutes": 15,
    "geometry": "..."
  }
}
```

---

#### `GET /api/maps/autocomplete/`

Get address suggestions.

**Query Parameters:**
- `input` (required): Search text

**Example:** `/api/maps/autocomplete/?input=Mumbai`

**Response:**
```json
{
  "success": true,
  "predictions": [
    {
      "description": "Mumbai, Maharashtra, India",
      "lat": 19.076,
      "lng": 72.8777,
      "place_id": "ChIJdd4hrwug2EcRmSrV3Vo6llI"
    }
  ]
}
```

---

## Ride Status Flow

```
requested → searching_driver → driver_assigned → driver_arriving → ride_started → ride_completed
                                       ↓
                                   cancelled
```

## Fare Calculation

Base fares and per-km rates:

| Vehicle Type | Base Fare | Per KM |
|--------------|-----------|--------|
| Mini         | ₹20       | ₹10    |
| Sedan        | ₹30       | ₹14    |
| SUV          | ₹40       | ₹18    |
| Auto         | ₹15       | ₹8     |
| Bike         | ₹10       | ₹6     |

---

## Admin Panel

Access at `/admin/` to:
- Approve/reject drivers
- View all rides
- Manage users
- View driver locations

---

## Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=True
OLA_CLIENT_ID=your-ola-client-id
OLA_CLIENT_SECRET=your-ola-client-secret
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890
```

---

## Frontend Integration

### Login Flow
1. Call `/api/auth/login/` with phone number
2. Get OTP (in dev mode: `123456`)
3. Call `/api/auth/verify/` with phone and OTP
4. Store user info from response

### Driver Flow
1. Register: `/api/drivers/register/`
2. Wait for admin approval in `/admin/`
3. Go online: `/api/drivers/toggle-online/`
4. Update location every 5 seconds: `/api/drivers/update-location/`
5. Accept rides: `/api/rides/accept/`
6. Update status: `/api/rides/update-status/`

### Passenger Flow
1. Login with OTP
2. Get nearby drivers: `/api/drivers/nearby/?lat=...&lng=...`
3. Request ride: `/api/rides/request/`
4. Track status: `/api/rides/status/{ride_id}/`

---

## Real-time Support (Future)

The project is prepared for Django Channels. To enable:

1. Install: `pip install channels channels-redis`
2. Set `ASGI_APPLICATION = 'rideapp.asgi.application'` in settings
3. Configure `CHANNEL_LAYERS` with Redis

For now, use polling (every 3-5 seconds) for:
- Driver location updates
- Ride status updates
