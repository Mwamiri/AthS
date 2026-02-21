"""
Request Validation Schemas
Pydantic models for API input validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {}
        }


# Authentication Schemas
class LoginSchema(BaseSchema):
    """Login request validation"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, max_length=255, description="User password")
    
    class Config:
        json_schema_extra = {
            'example': {
                'email': 'user@example.com',
                'password': 'securepassword123'
            }
        }


class RegisterSchema(BaseSchema):
    """User registration validation"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=255, description="Password (min 8 chars)")
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    
    @validator('password')
    def password_complexity(cls, v):
        """Validate password has mix of chars"""
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain uppercase, lowercase, and digits')
        return v
    
    class Config:
        json_schema_extra = {
            'example': {
                'email': 'newuser@example.com',
                'password': 'SecurePass123',
                'name': 'John Doe',
                'phone': '+1234567890'
            }
        }


class PasswordChangeSchema(BaseSchema):
    """Password change validation"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


# User Schemas
class UserBaseSchema(BaseSchema):
    """Base user schema"""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    role: str = Field(default='athlete', regex='^(admin|chief_registrar|registrar|starter|coach|athlete|viewer)$')
    is_active: bool = True


class UserCreateSchema(UserBaseSchema):
    """User creation schema"""
    password: str = Field(..., min_length=8)


class UserUpdateSchema(BaseSchema):
    """User update schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    role: Optional[str] = Field(None, regex='^(admin|chief_registrar|registrar|starter|coach|athlete|viewer)$')
    is_active: Optional[bool] = None


class UserResponseSchema(UserBaseSchema):
    """User response schema"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]


# Athlete Schemas
class AthleteBaseSchema(BaseSchema):
    """Base athlete schema"""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, regex='^(M|F|Other)$')
    club: Optional[str] = None
    registration_number: Optional[str] = None


class AthleteCreateSchema(AthleteBaseSchema):
    """Athlete creation schema"""
    user_id: Optional[int] = None


class AthleteUpdateSchema(BaseSchema):
    """Athlete update schema"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, regex='^(M|F|Other)$')
    club: Optional[str] = None
    registration_number: Optional[str] = None


class AthleteResponseSchema(AthleteBaseSchema):
    """Athlete response schema"""
    id: int
    user_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]


# Race Schemas
class RaceBaseSchema(BaseSchema):
    """Base race schema"""
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    date: datetime
    location: Optional[str] = None
    status: str = Field(default='scheduled', regex='^(scheduled|in_progress|completed|cancelled)$')


class RaceCreateSchema(RaceBaseSchema):
    """Race creation schema"""
    pass


class RaceUpdateSchema(BaseSchema):
    """Race update schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    status: Optional[str] = Field(None, regex='^(scheduled|in_progress|completed|cancelled)$')


class RaceResponseSchema(RaceBaseSchema):
    """Race response schema"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]


# Result Schemas
class ResultBaseSchema(BaseSchema):
    """Base result schema"""
    athlete_id: int = Field(..., description="Athlete ID")
    race_id: int = Field(..., description="Race ID")
    position: Optional[int] = Field(None, ge=1, description="Finishing position")
    time: Optional[str] = Field(None, description="Time (HH:MM:SS format)")
    points: Optional[int] = Field(None, ge=0, description="Points earned")
    status: str = Field(default='completed', regex='^(completed|disqualified|did_not_finish)$')


class ResultCreateSchema(ResultBaseSchema):
    """Result creation schema"""
    pass


class ResultUpdateSchema(BaseSchema):
    """Result update schema"""
    position: Optional[int] = Field(None, ge=1)
    time: Optional[str] = None
    points: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, regex='^(completed|disqualified|did_not_finish)$')


class ResultResponseSchema(ResultBaseSchema):
    """Result response schema"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]


# Pagination Schema
class PaginationSchema(BaseSchema):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: str = Field(default='asc', regex='^(asc|desc)$', description="Sort order")


# Response Schemas
class PaginatedResponseSchema(BaseSchema):
    """Paginated response wrapper"""
    data: List[dict]
    total: int
    page: int
    per_page: int
    total_pages: int


class ErrorResponseSchema(BaseSchema):
    """Error response schema"""
    error: str = Field(..., description="Error message")
    code: int = Field(..., description="Error code")
    details: Optional[dict] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now)


class SuccessResponseSchema(BaseSchema):
    """Success response schema"""
    message: str = Field(..., description="Success message")
    data: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)
