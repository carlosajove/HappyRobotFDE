# Local Analytics with Metabase

This directory contains the setup for running local analytics using Metabase with data from the HappyRobot FDE API.

## Overview

The local analytics workflow involves:

1. Syncing data from the production API to a local SQLite database
2. Running Metabase locally via Docker to visualize the data
3. Connecting Metabase to the local SQLite database

## Prerequisites

- Docker and Docker Compose installed
- Access to the HappyRobot FDE API (API key configured in main project `.env`)

## Quick Start

1. **Start everything (sync data + Metabase):**

   ```bash
   # From the project root directory
   docker compose -f docker-compose-metabase.yml up
   ```

   This will:
   - First sync data from the API to SQLite
   - Then start Metabase on <http://localhost:3000>

2. **Access Metabase at <http://localhost:3000>**

## Configuration

The sync script reads environment variables from the main project's `.env` file:

- `API_URL`: Your HappyRobot FDE API URL
- `API_KEY`: Your API key for authentication  
- `LOCAL_DB`: Path to the local SQLite database

## Metabase Setup

When first accessing Metabase:

1. Create an admin account on first run
2. Add a database:
   - Choose "SQLite" as database type
   - Set database file path to `/shared-data/analytics.db`
   - Name it "HappyRobot Analytics"
3. Create dashboards using the `loads` and `call_sessions` tables

## Database Schema

### Loads Table

- `load_id`: Primary key
- `origin`: Origin location  
- `destination`: Destination location
- `pickup_datetime`: Pickup date and time
- `delivery_datetime`: Delivery date and time
- `equipment_type`: Type of equipment needed
- `loadboard_rate`: Rate from loadboard
- `currency`: Currency of the rate
- `notes`: Additional notes
- `weight`: Load weight
- `weight_unit`: Unit of weight measurement
- `commodity_type`: Type of commodity
- `num_of_pieces`: Number of pieces
- `miles`: Distance in miles
- `dimensions`: Load dimensions
- `dimensions_unit`: Unit of dimension measurement
- `synced_at`: When data was last synced

### Call Sessions Table

- `id`: Primary key
- `call_id`: Unique call identifier
- `carrier_mc`: Carrier MC number
- `load_id`: Foreign key to loads table
- `original_rate`: Initial rate offered
- `final_rate`: Final negotiated rate
- `negotiation_count`: Number of negotiation rounds
- `outcome`: Call outcome (accepted, rejected, etc.)
- `sentiment`: Sentiment analysis result
- `duration`: Call duration in seconds
- `synced_at`: When data was last synced

## Commands Reference

All commands should be run from the project root directory:

```bash
# Start everything (sync + Metabase)
docker compose -f docker-compose-metabase.yml up

# Stop all services
docker compose -f docker-compose-metabase.yml down

# Re-sync data (stop and restart to refresh data)
docker compose -f docker-compose-metabase.yml down
docker compose -f docker-compose-metabase.yml up
```
