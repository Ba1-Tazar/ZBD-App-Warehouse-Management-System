from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

# --- SUPPLIER SCHEMAS ---

class SupplierBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    contact_email: Optional[str] = Field(None, pattern=r".*@.*")

class SupplierCreate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- LOCATION SCHEMAS ---

class LocationBase(BaseModel):
    zone_name: str = Field(..., min_length=1, max_length=10)
    shelf_number: int = Field(..., ge=1)

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- PRODUCT SCHEMAS ---

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1)
    sku: str = Field(..., min_length=3)
    price: Decimal = Field(Decimal("0.00"), ge=0)
    stock_quantity: int = Field(0, ge=0)

class ProductCreate(ProductBase):
    supplier_id: Optional[int] = None
    location_id: Optional[int] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    price: Optional[Decimal] = Field(None, ge=0)
    sku: Optional[str] = Field(None, min_length=3)
    supplier_id: Optional[int] = None
    location_id: Optional[int] = None

class ProductResponse(ProductBase):
    id: int
    supplier: Optional[SupplierResponse] = None
    location: Optional[LocationResponse] = None
    model_config = ConfigDict(from_attributes=True)

# --- WAREHOUSE LOG SCHEMAS ---

class WarehouseLogResponse(BaseModel):
    id: int
    action_type: str
    quantity_change: int
    created_at: datetime
    product_id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)
