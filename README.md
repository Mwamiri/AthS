# AthSys v2.2 🏃‍♂️

**Enterprise Athletics Management System | Production Ready**

[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)](https://redis.io/)

**Repository:** [Mwamiri/AthS](https://github.com/Mwamiri/AthS)  
**Developer:** Mwamiri  
**Version:** 2.2.0  
**Status:** ✅ Production Ready

## 📋 Overview

AthSys v2.2 is a comprehensive, enterprise-grade athletics management system designed for organizing track and field competitions at scale. Built for federation compliance, security, and performance, it handles athlete registration, real-time results processing, and comprehensive reporting.

**✨ Latest Release (v2.2.0):**
- ✅ **Modern Embedded Login**: Users log in directly on homepage via modal (no page redirect)
- ✅ **Beautiful Error Pages**: Modern graphical 404 page with suggestions and actions
- ✅ **Comprehensive Logging**: 5 log files with structured JSON output (athsys.log, errors, security, api)
- ✅ **CI/CD Pipeline**: Full GitHub Actions workflow for testing & deployment
- ✅ **PDF Report Generator**: Professional race, results, and statistics PDF exports
- ✅ **65+ Security Improvements**: Account lockout, rate limiting, CSRF protection, audit logs
- ✅ **8 Specialized Modules**: Search, export, async tasks, email, versioning, deduplication
- ✅ **41 API Endpoints**: Complete REST API for all operations
- ✅ **PostgreSQL + Redis**: Enterprise-grade database and caching

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 16+
- Redis 7+ (optional but recommended)
- Docker & Docker Compose (for containerized deployment)

### Local Development
```bash
# Clone repository
git clone https://github.com/Mwamiri/AthS.git
cd AthSys_ver1

# Install dependencies
cd src/backend
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://athsys_user:athsys_pass@localhost:5432/athsys_db
export REDIS_URL=redis://localhost:6379/0

# Run development server
python app.py
```

Then visit: **http://localhost:5000**

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Logs
docker-compose logs -f web
```

### Production Deployment
```bash
# Install production WSGI server
pip install gunicorn

# Run with Gunicorn (4 workers)
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app

# Or via Docker (recommended)
docker-compose -f docker-compose.yml up -d
```

## 🔐 Security Features

✅ **Authentication & Authorization**
- bcrypt password hashing with salt
- Account lockout (5 failed attempts → 30 min suspension)
- Session-based authentication with Redis
- Role-based access control (7 roles: admin, coach, official, athlete, registrar, chief_registrar, viewer)
- Token-based API authorization

✅ **Data Protection**
- CSRF token validation
- SQL injection prevention via SQLAlchemy ORM
- Input sanitization and validation
- XSS protection headers
- Password strength requirements (8+ chars, uppercase, lowercase, numbers, special)

✅ **Monitoring & Audit**
- Complete audit logging of all user actions
- Failed login tracking
- Security event monitoring
- Request ID tracking for debugging
- Rate limiting (configurable per endpoint)

✅ **Infrastructure Security**
- Security headers (X-Frame-Options, X-Content-Type-Options, CSP, HSTS)
- CORS configuration
- Referrer Policy enforcement
- Permissions Policy headers

## ✨ Key Features

### 🎯 Core Functionality
- **Athlete Management**: Profiles, contact info, club associations
- **Race Organization**: Event scheduling, bib allocation, registration
- **Results Tracking**: Multiple timing methods, final standings
- **Real-time Updates**: Redis-powered live data streaming
- **Data Export**: CSV/Excel exports for athletes, results, registrations

### 🔍 Advanced Features
- **Full-Text Search**: Search athletes, races, events by name or location
- **Faceted Filtering**: Filter by status, category, date range, distance
- **Autocomplete**: Smart suggestions while typing
- **Asynchronous Tasks**: Background job queue for email, exports, reports
- **Email Notifications**: SendGrid/SMTP integration with templates

### 📊 Reporting
- **Professional PDFs**: Race reports, results, statistics
- **Structured Logging**: JSON + text output with rotation
- **Real-time Logs Viewer**: Filter and search logs in browser
- **System Health Dashboard**: Monitor all components

### 🧩 Extensibility
- **Plugin System**: Enable/disable plugins without code changes
- **API Versioning**: v1/v2 support with deprecation headers
- **Webhook Support**: External system integration
- **Custom Fields**: Add fields per organization needs
  - Core: Authentication, User Management, Race Management
  - Enterprise: Audit Logging, Email, Health Monitoring, Feature Flags, Request Deduplication
  - Features: Official Timing, Athlete Registration, Analytics, Leaderboard, Reports
  - Security: 2FA, RBAC
  - Infrastructure: Database Migrations, CI/CD Pipeline
- **Plugin Admin Dashboard**: Full control over system features

### 💾 Data Management
- **PostgreSQL Database**: Relational data with ACID compliance
- **Redis Caching**: Sub-millisecond data access for frequently used queries
- **Auto Backup**: Scheduled automatic database backups
- **Self-Healing**: Automated error detection and recovery
- **Multi-Format Export**:
  - Excel spreadsheets
  - HTML reports
  - XML/JSON for federation compliance

## 🏗️ Architecture

```
AthSys_ver1/
├── src/
│   ├── backend/          # Backend API services
│   │   ├── app.py        # Main Flask application
│   │   ├── models.py     # Database models
│   │   ├── plugin_manager.py  # Plugin system
│   │   └── config.py     # Configuration
│   ├── frontend/         # Web interface
│   │   ├── index.html    # Landing page
│   │   ├── login.html    # Authentication
│   │   ├── plugins-admin.html  # Plugin management
│   │   ├── official-timing.html # Timing interface
│   │   ├── races-results.html   # Public portal
│   │   └── ...
│   ├── mobile/           # Mobile applications
│   └── plugins/          # Plugin modules
├── config/
│   └── nginx/            # Web server configuration
├── scripts/              # Utility scripts
├── self_healing/         # Health monitoring
├── tests/                # Test suites
├── docs/                 # Documentation
└── docker-compose.yml    # Container orchestration
```

## 🛠️ Technology Stack

- **Backend**: Python 3.11, Flask 3.0
- **Frontend**: Modern JavaScript framework, HTML5, CSS3
- **Database**: PostgreSQL 16, Redis 7
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx
- **Authentication**: JWT, TOTP (2FA), bcrypt
- **Monitoring**: Custom health checks, Prometheus-ready

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Mwamiri/AthS.git
cd AthS
```

2. Start with Docker Compose:
```bash
docker-compose up -d
```

3. Access the application:
```
http://localhost
```

## � API Endpoints

AthSys provides 41 RESTful API endpoints organized by feature:

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Token refresh
- `GET /api/auth/verify` - Verify current user
- `POST /api/auth/2fa/setup` - Enable 2FA
- `POST /api/auth/2fa/verify` - Verify 2FA code
- `POST /api/auth/password-reset` - Request password reset
- `POST /api/auth/password-reset/confirm` - Confirm password reset

### Athlete Management
- `GET /api/athletes` - List athletes
- `GET /api/athletes/<id>` - Get athlete details
- `POST /api/athletes` - Create athlete
- `PUT /api/athletes/<id>` - Update athlete
- `DELETE /api/athletes/<id>` - Delete athlete
- `GET /api/athletes/<id>/races` - Get athlete's races
- `GET /api/athletes/<id>/results` - Get athlete's results
- `POST /api/athletes/<id>/export` - Export athlete data

### Race Management
- `GET /api/races` - List races
- `GET /api/races/<id>` - Get race details
- `POST /api/races` - Create race
- `PUT /api/races/<id>` - Update race
- `DELETE /api/races/<id>` - Delete race
- `POST /api/races/<id>/publish` - Publish race
- `POST /api/races/<id>/archive` - Archive race
- `GET /api/races/<id>/events` - Get race events

### Results Management
- `GET /api/results` - List results
- `GET /api/results/<id>` - Get result details
- `POST /api/results` - Record result
- `PUT /api/results/<id>` - Update result
- `DELETE /api/results/<id>` - Delete result
- `POST /api/results/bulk` - Bulk import results
- `GET /api/results/export` - Export results

### Admin Operations
- `GET /api/admin/dashboard` - System dashboard
- `GET /api/admin/logs` - View system logs
- `POST /api/admin/backup` - Trigger database backup
- `POST /api/admin/plugins/<name>/toggle` - Toggle plugin
- `GET /api/admin/users` - List all users
- `POST /api/admin/users/<id>/ban` - Ban user

### Statistics & Analytics
- `GET /api/stats/system` - System statistics
- `GET /api/stats/races` - Race statistics
- `GET /api/stats/athletes` - Athlete statistics
- `POST /api/reports/pdf` - Generate PDF report

All endpoints require authentication (JWT token) unless otherwise specified.

## 📖 Documentation

Detailed documentation is available in the `/docs` directory:
- Installation Guide
- User Manual
- API Reference
- Plugin Development Guide
- See also: [COMPLETION_REPORT.md](COMPLETION_REPORT.md) for comprehensive implementation details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Mwamiri**
- Domain: [appstore.co.ke](https://appstore.co.ke)
- GitHub: [@Mwamiri](https://github.com/Mwamiri)

## 🙏 Acknowledgments

- World Athletics for competition standards
- Athletics federations for compliance requirements
- Open source community for tools and libraries

## 📞 Support

For support and inquiries:
- Visit: [appstore.co.ke](https://appstore.co.ke)
- Open an issue on GitHub

---

**Built with ❤️ for the athletics community**
