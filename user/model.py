from tortoise import fields, models
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

# ------------------------------------------------------------------------------------
#                                   MODELS
# ------------------------------------------------------------------------------------

# --- USERS ---
class User(models.Model):
    id = fields.IntField(pk=True)
    login = fields.CharField(max_length=100, unique=True)
    password = fields.CharField(max_length=255)
    is_admin = fields.BooleanField(default=False)

    class Meta:
        table = "users"

# --- SUPPLIERS ---
class Supplier(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    contact_email = fields.CharField(max_length=100, null=True)

    class Meta:
        table = "suppliers"

# --- LOCATIONS ---
class Location(models.Model):
    id = fields.IntField(pk=True)
    zone_name = fields.CharField(max_length=10) # e.g. 'A'
    shelf_number = fields.IntField() # e.g. 5
    
    class Meta:
        table = "locations"
        # Prevents duplicate storage locations (e.g., Zone A, Shelf 5)
        unique_together = (("zone_name", "shelf_number"),)

# --- PRODUCTS ---
class Product(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    sku = fields.CharField(max_length=50, unique=True)
    price = fields.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock_quantity = fields.IntField(default=0)
    
    supplier = fields.ForeignKeyField("models.Supplier", related_name="products", null=True)
    location = fields.ForeignKeyField("models.Location", related_name="products", null=True)

    class Meta:
        table = "products"

# --- LOGS ---
class WarehouseLog(models.Model):
    id = fields.IntField(pk=True)
    action_type = fields.CharField(max_length=20) # e.g. IN, OUT, MOVE
    quantity_change = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)

    user = fields.ForeignKeyField("models.User", related_name="logs")
    product = fields.ForeignKeyField("models.Product", related_name="logs")

    class Meta:
        table = "warehouse_logs"

# ------------------------------------------------------------------------------------
#                                   SCHEMAS
# ------------------------------------------------------------------------------------ 

# --- USER SCHEMAS ---
class UserSchema(BaseModel):
    id: Optional[int] = None
    login: str
    password: str
    is_admin: Optional[bool] = False

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "login": "warehouse_worker",
                "password": "securepassword123"
            }
        }
    }

# --- SUPPLIER SCHEMAS ---
class SupplierSchema(BaseModel):
    """Base fields for warehouse suppliers."""
    name: str
    contact_email: Optional[str] = None

class SupplierCreate(SupplierSchema):
    """Schema for creating or updating a supplier. No ID field included."""
    pass

class SupplierResponse(SupplierSchema):
    """Schema for supplier responses, including the database-generated ID."""
    id: int

    model_config = {"from_attributes": True}


# --- LOCATION SCHEMAS ---
class LocationSchema(BaseModel):
    """Base fields for warehouse locations."""
    zone_name: str
    shelf_number: int

class LocationCreate(LocationSchema):
    """Schema for creating or updating a location. No ID field included."""
    pass

class LocationResponse(LocationSchema):
    """Schema for location responses, including the database-generated ID."""
    id: int

    model_config = {"from_attributes": True}

# --- PRODUCT SCHEMAS ---
class ProductSchema(BaseModel):
    name: str
    sku: str
    price: Decimal = Decimal("0.00")
    stock_quantity: int = 0
    supplier_id: Optional[int] = None
    location_id: Optional[int] = None
    

class ProductCreate(ProductSchema):
    """Schema for creating or updating a product. No ID field included."""
    pass

class ProductUpdate(BaseModel):
    """Schema for partial product updates. All fields are optional."""
    name: Optional[str] = None
    price: Optional[float] = None
    sku: Optional[str] = None
    supplier_id: Optional[int] = None
    location_id: Optional[int] = None

class ProductResponse(ProductSchema):
    """Schema for product responses, including the database-generated ID."""
    id: int

    model_config = {"from_attributes": True}

# --- LOG SCHEMAS ---
class WarehouseLogSchema(BaseModel):
    id: Optional[int] = None
    action_type: str
    quantity_change: int
    created_at: Optional[datetime] = None
    product_id: int
    user_id: int

    model_config = {"from_attributes": True}
