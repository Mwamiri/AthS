# AthSys ver1 🏃‍♂️

**Enterprise Athletics Management System**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org/)

**Domain:** [appstore.co.ke](https://appstore.co.ke)  
**Developer:** Mwamiri  
**Version:** 1.0.0

## 📋 Overview

AthSys is a comprehensive, enterprise-grade athletics management system designed for organizing and managing track and field competitions. Built for federation compliance and scalability, it handles everything from athlete registration to real-time results processing and export.

## ✨ Key Features

### 🎯 Competition Management
- **Athlete Registration**: Complete athlete profiles with optional World Athletics codes
- **Bib Assignment**: Automated bib number allocation and conflict resolution
- **Event Management**: Multi-event competition support with scheduling

### 📊 Results Processing
- **Multiple Input Methods**: 
  - Real-time timing mat integration
  - Manual entry interface
  - Bulk import capabilities
- **Performance Tracking**:
  - Personal Bests (PB) calculation
  - Season Bests (SB) tracking
  - Team scoring and rankings

### 🔌 Extensibility
- **Plugin Ecosystem**: Modular architecture for custom extensions
- **Tabbed Management Interface**: Intuitive plugin control panel
- **API Support**: RESTful endpoints for third-party integrations

### 💾 Data Management
- **Auto Backup**: Scheduled automatic backups
- **Self-Healing**: Automated error detection and recovery
- **Multi-Format Export**:
  - Excel spreadsheets
  - HTML reports
  - XML/JSON for federation compliance

### 🚀 Deployment
- **Docker Support**: Containerized deployment for easy scaling
- **Coolify Integration**: One-click cloud deployment
- **Nginx Configuration**: Production-ready web server setup

## 🏗️ Architecture

```
AthSys_ver1/
├── src/
│   ├── backend/          # Backend API services
│   ├── frontend/         # Web interface
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

- **Backend**: Python, FastAPI/Django
- **Frontend**: Modern JavaScript framework
- **Database**: PostgreSQL/MySQL
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx
- **Monitoring**: Custom health checks

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

## 📖 Documentation

Detailed documentation is available in the `/docs` directory:
- Installation Guide
- User Manual
- API Reference
- Plugin Development Guide

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
