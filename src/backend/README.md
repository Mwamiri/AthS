# AthSys Backend

Flask-based REST API for the Athletics Management System.

## Features
- Athlete registration and management
- Event scheduling
- Results tracking
- Federation-compliant data exports

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /api/athletes` - List athletes
- `POST /api/athletes` - Create athlete
- `GET /api/events` - List events
- `GET /api/results` - Get results
- `GET /api/stats` - System statistics
