# AthS Backend

Flask-based REST API for the Athletics Management System.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export SECRET_KEY=your-secret-key-min-32-chars
export DATABASE_URL=postgresql://user:password@localhost:5432/aths_db
export JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars
```

4. Run development server:
```bash
flask run
```

## Testing

```bash
pytest --cov=.
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/data/athletes` - List athletes
- `GET /api/data/events` - List events
- `GET /api/data/performances` - List performances
- `GET /api/data/competitions` - List competitions
- `GET /api/data/summary` - Dashboard summary

## Configuration

See `config.py` for configuration options. All settings can be overridden via environment variables.

## Logging

Structured JSON logging is enabled by default. Logs are written to stdout.
