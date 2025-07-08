# HappyRobot FDE – Inbound Carrier Campaign

A FastAPI-based system for handling inbound carrier calls, load bookings, and analytics visualization through HappyRobot platform integration.

## Features

- 🚛 **Load & Call Management**: Handle inbound carrier calls with negotiation logic
- 📊 **Analytics Dashboard**: Metabase integration for data visualization  
- 🔐 **API Security**: API key authentication for all endpoints
- 🚀 **Cloud Ready**: Fly.io deployment with Docker containerization
- ✅ **FMCSA Integration**: Real-time carrier verification

# Start

## Setup

```bash
# Clone repository
git clone <repository>
cd HappyRobotFDE

# Create .env file by copying .env.example and providing the parameters

```

## Deployment

### App Production (Fly.io)

```bash
# Prerequisite: you must have fly.io installed and logged in
flyctl deploy
flyctl secrets set API_KEY="your_key" FMCSA_API_KEY="your_key" # (only the first time)

# populate the database with demo-data
curl -X POST https://happyrobot-fde.fly.dev/populate-all-demo-data -H "api-key: 123454321"

```
⚠️ **Warning**: In production the app uses an in‑memory database, so data is lost whenever the instance restarts or the host sleeps. Reload the demo data before each run.

### Local Analytics

```bash
# Create the ssl certificates for a secure connection (only the first time)
mkdir -p ssl
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -subj "/CN=localhost"


# Start Metabase + Analytics Sync
docker compose -f docker-compose-metabase.yml up -d

# Sync data from API to local database
curl -H "api-key: $SYNC_API_KEY" -X POST http://localhost:8001/sync

# Access Metabase: http://localhost:3000
# Locally-run Metabase doesn't allow to export dashboard configurations, 
# therefore you must perform your own set-up (only the first time)
```

## Architecture

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │────│  Analytics API  │────│   Sync Service  │
│   (Port 8080)   │    │                 │    │   (Port 8001)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         │                                              ▼
         ▼                                    ┌─────────────────┐
┌─────────────────┐                          │   SQLite DB     │
│   Production    │                          │  (analytics.db) │
│   Database      │                          └─────────────────┘
└─────────────────┘                                   │
                                                      ▼
                                            ┌─────────────────┐
                                            │    Metabase     │
                                            │   Dashboard     │
                                            │  (Port 3000)    │
                                            └─────────────────┘
```

## Call Flow

1. **Verify Carrier** → FMCSA API validation
2. **Search Loads** → Match carrier preferences  
3. **Negotiate** → Handle up to 3 counter offers
4. **Close Deal** → Extract outcome and sentiment
5. **Analytics** → Track metrics in Metabase


## API Endpoints

### Core API

- `GET /health` - Health check
- `GET /loads` - Search loads (requires API key)
- `GET /verify-mc?mc={number}` - Verify carrier MC
- `POST /call/counter-offer` - Handle negotiations

### Analytics API

- `GET /analytics/loads` - Export loads data
- `GET /analytics/calls` - Export call sessions data

### Sync Service

- `GET /status` - Check sync service status
- `POST /sync` - Sync data to local analytics DB



### Local Development (APP)

```bash
# activate your virtual env then:
# Install dependencies
pip install -r requirements.txt

# Run FastAPI app
python -m app.main
# Access: http://localhost:8080/docs


#or you can run a docker container
docker compose up -d
```