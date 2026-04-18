"""
models.py
Pydantic request and response models for the FastAPI app.

Pydantic validates all incoming data automatically.
If a field is wrong type or missing, FastAPI returns a 422 error before
the endpoint function even runs.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# ── Item models ───────────────────────────────────────────────────────────────

class ItemCreate(BaseModel):
    """Request body for creating an item."""
    name:        str         = Field(..., min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, max_length=500)
    price:       float       = Field(..., gt=0, description="Price must be positive")
    category:    str         = Field(..., description="Category: electronics / food / clothing / other")
    in_stock:    bool        = Field(True)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        allowed = {"electronics", "food", "clothing", "other"}
        if v.lower() not in allowed:
            raise ValueError(f"category must be one of {allowed}")
        return v.lower()

    @field_validator("name")
    @classmethod
    def strip_name(cls, v):
        return v.strip()

    model_config = {"json_schema_extra": {"example": {
        "name": "Wireless Headphones",
        "description": "Noise-cancelling over-ear headphones",
        "price": 2999.99,
        "category": "electronics",
        "in_stock": True,
    }}}


class ItemResponse(BaseModel):
    """Response model for a single item."""
    id:          int
    name:        str
    description: Optional[str]
    price:       float
    category:    str
    in_stock:    bool
    created_at:  datetime


class ItemListResponse(BaseModel):
    """Paginated list of items."""
    items:   list[ItemResponse]
    total:   int
    page:    int
    per_page: int
    pages:   int


# ── User / auth models ────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str  = Field(..., min_length=3, max_length=30)
    email:    str  = Field(..., pattern=r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
    age:      Optional[int] = Field(None, ge=0, le=150)

    model_config = {"json_schema_extra": {"example": {
        "username": "pradhnyesh",
        "email":    "pradhnyesh@example.com",
        "age":      22,
    }}}


class UserResponse(BaseModel):
    id:       int
    username: str
    email:    str
    age:      Optional[int]


# ── Background task model ─────────────────────────────────────────────────────

class EmailRequest(BaseModel):
    to:      str = Field(..., pattern=r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
    subject: str = Field(..., min_length=1, max_length=200)
    body:    str = Field(..., min_length=1)


# ── Generic response models ───────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    detail:    str
    error_code: str
