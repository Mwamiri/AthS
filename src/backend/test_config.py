"""
Testing Configuration and Utilities
Pytest setup and test fixtures for unit and integration tests
"""

import pytest
import os
import sys
from datetime import datetime
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Test configuration
class TestConfig:
    """Test environment configuration"""
    TESTING = True
    FLASK_ENV = 'testing'
    DATABASE_URL = 'sqlite:///:memory:'
    REDIS_URL = 'redis://localhost:6379/1'
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    RATELIMIT_ENABLED = False


@pytest.fixture(scope='session')
def app():
    """Create Flask application for testing"""
    from config import BaseConfig
    from app import create_app
    
    # Create app with test config
    app = create_app()
    app.config.from_object(TestConfig)
    
    return app


@pytest.fixture(scope='session')
def client(app):
    """Test client fixture"""
    with app.app_context():
        yield app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Database session fixture for each test"""
    from models import Base, get_db
    
    with app.app_context():
        # Create tables
        Base.metadata.create_all(bind=get_db().get_bind())
        session = get_db()
        
        yield session
        
        # Cleanup
        Base.metadata.drop_all(bind=get_db().get_bind())
        session.rollback()


@pytest.fixture
def auth_headers(client):
    """Generate authentication headers for testing"""
    token = generate_test_token({'user_id': 1, 'role': 'admin'})
    return {'Authorization': f'Bearer {token}'}


def generate_test_token(payload: dict, app_secret: str = 'test-jwt-secret') -> str:
    """Generate JWT token for testing"""
    import jwt
    from datetime import datetime, timedelta
    
    payload.update({
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=1)
    })
    
    return jwt.encode(payload, app_secret, algorithm='HS256')


class TestDataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_user(session: Session, **kwargs):
        """Create test user"""
        from models import User
        
        user = User(
            email=kwargs.get('email', f'test-{datetime.now().timestamp()}@example.com'),
            password_hash=kwargs.get('password_hash', 'hashed_password'),
            name=kwargs.get('name', 'Test User'),
            role=kwargs.get('role', 'athlete'),
            is_active=kwargs.get('is_active', True)
        )
        session.add(user)
        session.commit()
        return user
    
    @staticmethod
    def create_athlete(session: Session, user_id: int = None, **kwargs):
        """Create test athlete"""
        from models import Athlete
        
        athlete = Athlete(
            user_id=user_id,
            first_name=kwargs.get('first_name', 'Test'),
            last_name=kwargs.get('last_name', 'Athlete'),
            gender=kwargs.get('gender', 'M'),
            club=kwargs.get('club', 'Test Club')
        )
        session.add(athlete)
        session.commit()
        return athlete
    
    @staticmethod
    def create_race(session: Session, **kwargs):
        """Create test race"""
        from models import Race
        
        race = Race(
            name=kwargs.get('name', 'Test Race'),
            description=kwargs.get('description', 'Test Description'),
            date=kwargs.get('date', datetime.utcnow()),
            location=kwargs.get('location', 'Test Location'),
            status=kwargs.get('status', 'scheduled')
        )
        session.add(race)
        session.commit()
        return race
    
    @staticmethod
    def create_result(session: Session, athlete_id: int, race_id: int, **kwargs):
        """Create test result"""
        from models import Result
        
        result = Result(
            athlete_id=athlete_id,
            race_id=race_id,
            position=kwargs.get('position'),
            time=kwargs.get('time'),
            points=kwargs.get('points', 0),
            status=kwargs.get('status', 'completed')
        )
        session.add(result)
        session.commit()
        return result


# Test base classes
class BaseAPITest:
    """Base class for API tests"""
    
    def assert_status_code(self, response, expected_code):
        """Assert response status code"""
        assert response.status_code == expected_code, \
            f'Expected {expected_code}, got {response.status_code}: {response.get_json()}'
    
    def assert_success(self, response):
        """Assert successful response"""
        self.assert_status_code(response, 200)
        data = response.get_json()
        assert data.get('success') is True, f'Response not marked as success: {data}'
    
    def assert_error(self, response, status_code=400):
        """Assert error response"""
        self.assert_status_code(response, status_code)
        data = response.get_json()
        assert 'error' in data, f'No error field in response: {data}'
    
    def assert_has_field(self, data, field):
        """Assert response has field"""
        assert field in data, f'Field "{field}" not found in response: {list(data.keys())}'
    
    def assert_pagination(self, response):
        """Assert pagination structure"""
        self.assert_success(response)
        data = response.get_json()
        assert 'pagination' in data, 'No pagination in response'
        assert 'total' in data['pagination']
        assert 'page' in data['pagination']
        assert 'per_page' in data['pagination']


# pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Collection hooks
def pytest_collection_modifyitems(config, items):
    """Add markers to tests"""
    for item in items:
        # Mark tests based on filename
        if 'test_unit' in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif 'test_integration' in str(item.fspath):
            item.add_marker(pytest.mark.integration)
