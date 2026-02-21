"""
Swagger/OpenAPI API Documentation
Auto-generated API documentation with Flasgger
"""

from flask import Flask
from flasgger import Swagger
from flask_swagger_ui import get_swaggerui_blueprint


def setup_swagger(app: Flask):
    """Initialize Swagger/OpenAPI documentation"""
    
    # Swagger configuration
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda x: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs",
        "title": "AthSys API v2.1",
        "uiversion": 4
    }
    
    swagger = Swagger(app, config=swagger_config)
    
    # Set up Swagger UI
    swaggerui_blueprint = get_swaggerui_blueprint(
        '/api/swagger',
        '/apispec.json',
        config={'app_name': 'AthSys API'}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix='/api/swagger')
    
    return swagger


# API Documentation Templates

AUTH_DOCS = {
    'tags': ['Authentication'],
    'definitions': {
        'LoginRequest': {
            'type': 'object',
            'required': ['email', 'password'],
            'properties': {
                'email': {'type': 'string', 'example': 'user@example.com'},
                'password': {'type': 'string', 'example': 'password123'}
            }
        },
        'AuthResponse': {
            'type': 'object',
            'properties': {
                'token': {'type': 'string', 'description': 'JWT access token'},
                'refresh_token': {'type': 'string', 'description': 'JWT refresh token'},
                'user': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'email': {'type': 'string'},
                        'name': {'type': 'string'},
                        'role': {'type': 'string'}
                    }
                }
            }
        }
    }
}

USER_DOCS = {
    'tags': ['Users'],
    'definitions': {
        'User': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'email': {'type': 'string'},
                'name': {'type': 'string'},
                'phone': {'type': 'string'},
                'role': {'type': 'string', 'enum': ['admin', 'chief_registrar', 'registrar', 'starter', 'coach', 'athlete']},
                'is_active': {'type': 'boolean'},
                'created_at': {'type': 'string', 'format': 'date-time'},
                'updated_at': {'type': 'string', 'format': 'date-time'}
            }
        }
    }
}

ATHLETE_DOCS = {
    'tags': ['Athletes'],
    'definitions': {
        'Athlete': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'},
                'date_of_birth': {'type': 'string', 'format': 'date'},
                'gender': {'type': 'string', 'enum': ['M', 'F', 'Other']},
                'club': {'type': 'string'},
                'registration_number': {'type': 'string'},
                'created_at': {'type': 'string', 'format': 'date-time'}
            }
        }
    }
}

RACE_DOCS = {
    'tags': ['Races'],
    'definitions': {
        'Race': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'string'},
                'description': {'type': 'string'},
                'date': {'type': 'string', 'format': 'date-time'},
                'location': {'type': 'string'},
                'status': {'type': 'string', 'enum': ['scheduled', 'in_progress', 'completed', 'cancelled']},
                'created_at': {'type': 'string', 'format': 'date-time'}
            }
        }
    }
}

RESULT_DOCS = {
    'tags': ['Results'],
    'definitions': {
        'Result': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'athlete_id': {'type': 'integer'},
                'race_id': {'type': 'integer'},
                'position': {'type': 'integer'},
                'time': {'type': 'string', 'example': '00:45:30'},
                'points': {'type': 'integer'},
                'status': {'type': 'string', 'enum': ['completed', 'disqualified', 'did_not_finish']},
                'created_at': {'type': 'string', 'format': 'date-time'}
            }
        }
    }
}

ERROR_RESPONSE = {
    'type': 'object',
    'properties': {
        'error': {'type': 'string'},
        'code': {'type': 'integer'},
        'error_type': {'type': 'string'},
        'details': {'type': 'object'},
        'timestamp': {'type': 'string', 'format': 'date-time'}
    }
}

SUCCESS_RESPONSE = {
    'type': 'object',
    'properties': {
        'message': {'type': 'string'},
        'data': {'type': 'object'},
        'timestamp': {'type': 'string', 'format': 'date-time'}
    }
}

PAGINATED_RESPONSE = {
    'type': 'object',
    'properties': {
        'data': {'type': 'array', 'items': {'type': 'object'}},
        'pagination': {
            'type': 'object',
            'properties': {
                'total': {'type': 'integer'},
                'page': {'type': 'integer'},
                'per_page': {'type': 'integer'},
                'total_pages': {'type': 'integer'}
            }
        }
    }
}


def get_endpoint_doc(
    summary: str,
    description: str,
    tags: list,
    request_body: dict = None,
    responses: dict = None,
    parameters: list = None,
    security: list = None
) -> dict:
    """Generate endpoint documentation"""
    doc = {
        'summary': summary,
        'description': description,
        'tags': tags,
        'responses': responses or {
            '200': {'description': 'Success'},
            '400': {'description': 'Bad Request'},
            '401': {'description': 'Unauthorized'},
            '500': {'description': 'Internal Server Error'}
        }
    }
    
    if request_body:
        doc['parameters'] = [{
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': request_body
        }]
    
    if parameters:
        if 'parameters' not in doc:
            doc['parameters'] = []
        doc['parameters'].extend(parameters)
    
    if security:
        doc['security'] = security
    
    return doc
