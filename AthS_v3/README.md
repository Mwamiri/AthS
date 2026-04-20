# AthS v3.0.0 - Athletics Management System

## Overview

AthS is a production-ready athletics management system built with modern technologies for tracking athlete performance, managing competitions, and generating comprehensive reports.

## Features

- **Athlete Management**: Track athlete profiles, personal records, and training history
- **Competition Tracking**: Manage events, results, and rankings
- **Performance Analytics**: Interactive charts and visualizations
- **Multi-theme UI**: Light, Dark, and Ocean themes with glassmorphism design
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Security**: JWT authentication, rate limiting, HTTPS enforcement
- **Caching**: Redis-backed caching for improved performance
- **Monitoring**: Health checks and structured logging

## Tech Stack

### Backend
- Python 3.11
- Flask 3.0.3
- PostgreSQL 16
- Redis 7
- Gunicorn WSGI server

### Frontend
- Vue 3.4 with TypeScript
- Vite 5.2
- Tailwind CSS 3.4
- Chart.js 4.4
- TanStack Query

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AthS_v3
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start all services:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost
- Backend API: http://localhost:5000/api

## Project Structure

```
AthS_v3/
├── src/backend/          # Flask backend application
│   ├── api/              # API endpoints
│   ├── models/           # SQLAlchemy models
│   ├── tests/            # Unit tests
│   ├── app.py            # Application factory
│   ├── config.py         # Configuration management
│   └── requirements.txt  # Python dependencies
├── src/frontend/         # Vue.js frontend application
│   ├── src/
│   │   ├── components/   # Reusable Vue components
│   │   ├── views/        # Page components
│   │   ├── layouts/      # Layout components
│   │   ├── router/       # Vue Router configuration
│   │   ├── lib/          # Utilities and API client
│   │   └── composables/  # Vue composables
│   ├── package.json      # Node dependencies
│   └── vite.config.ts    # Vite configuration
├── docker-compose.yml    # Docker orchestration
├── Dockerfile.backend    # Backend container definition
└── Dockerfile.frontend   # Frontend container definition
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/data/athletes` - List athletes
- `GET /api/data/events` - List events
- `GET /api/data/performance` - Performance metrics

## Development

### Backend Development

```bash
cd src/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run
```

### Frontend Development

```bash
cd src/frontend
npm install
npm run dev
```

## Testing

### Backend Tests
```bash
cd src/backend
pytest
```

### Frontend Tests
```bash
cd src/frontend
npm run test
```

## Security

- Change default SECRET_KEY and JWT_SECRET_KEY in production
- Enable HTTPS in production (set FORCE_HTTPS=true)
- Review SECURITY.md for detailed security guidelines
- Keep dependencies updated using Dependabot

## Monitoring

- Health checks configured for all services
- Structured JSON logging enabled
- Redis and PostgreSQL monitoring via health endpoints

## License

MIT License

## Support

For issues and feature requests, please open an issue on GitHub.
