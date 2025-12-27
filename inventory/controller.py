from fastapi import APIRouter, Depends, HTTPException
from user.model import (
    Supplier, SupplierSchema, 
    Location, LocationSchema, 
    Product, ProductSchema,
    User
)
from user.auth import get_admin_user, get_current_user

router = APIRouter()

# ----------------------------------------------------------------------------------
#                                 SUPPLIERS
# ----------------------------------------------------------------------------------

# -- ADMIN --
@router.post("/suppliers", response_model=SupplierSchema, status_code=201, tags=["Inventory: Suppliers"])
async def create_supplier(data: SupplierSchema, admin: User = Depends(get_admin_user)):
    """Add a new supplier to the system."""
    return await Supplier.create(**data.model_dump(exclude={"id"}))


# -- USER --
@router.get("/suppliers", response_model=list[SupplierSchema], tags=["Inventory: Suppliers"])
async def list_suppliers(current_user: User = Depends(get_current_user)):
    """List all suppliers (Available to all logged-in users)."""
    return await Supplier.all()

# ----------------------------------------------------------------------------------
#                                 LOCATIONS
# ----------------------------------------------------------------------------------

# -- ADMIN --
@router.post("/locations", response_model=LocationSchema, status_code=201, tags=["Inventory: Locations"])
async def create_location(data: LocationSchema, admin: User = Depends(get_admin_user)):
    """Define a new warehouse slot (Zone + Shelf)."""
    # Check for duplicates manually to provide a nice error message
    existing = await Location.get_or_none(zone_name=data.zone_name, shelf_number=data.shelf_number)
    if existing:
        raise HTTPException(status_code=400, detail="Location already exists")
    
    return await Location.create(**data.model_dump(exclude={"id"}))

# ----------------------------------------------------------------------------------
#                                 PRODUCTS
# ----------------------------------------------------------------------------------

# -- ADMIN --
@router.post("/products", response_model=ProductSchema, status_code=201, tags=["Inventory: Products"])
async def create_product(data: ProductSchema, admin: User = Depends(get_admin_user)):
    """Create a product and link it to a supplier and location."""
    # Logic to ensure the supplier and location IDs actually exist
    if not await Supplier.exists(id=data.supplier_id):
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    return await Product.create(**data.model_dump(exclude={"id"}))
