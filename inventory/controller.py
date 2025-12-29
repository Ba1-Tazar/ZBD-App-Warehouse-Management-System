from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import List

from .model import Product, Supplier, Location, WarehouseLog
from .schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    SupplierCreate, SupplierResponse,
    LocationCreate, LocationResponse,
    WarehouseLogResponse
)

# Importy z modułu user (tylko to, co dotyczy użytkownika i sesji)
from user.model import User
from user.auth import get_admin_user, get_current_user

from .service import WarehouseService
from datetime import datetime
from enum import Enum

router = APIRouter()

class ActionType(str, Enum):
    IN = "IN"
    OUT = "OUT"

# ----------------------------------------------------------------------------------
#                                 OPERATIONS
# ----------------------------------------------------------------------------------

# -- USER --
# Handle stock adjustments (e.g., receiving or releasing goods)
@router.post("/products/{product_id}/adjust", tags=["Inventory: Operations"])
async def adjust_product_stock(
    product_id: int, 
    amount: int, 
    action: ActionType, # Expected values: "IN" or "OUT"
    current_user: User = Depends(get_current_user)):
    """
    Update stock levels via WarehouseService with automated transaction logging.
    """
    try:
        updated_product = await WarehouseService.adjust_stock(
            product_id=product_id, 
            user=current_user, 
            amount=amount, 
            action=action.value # .value wyciągnie czysty tekst "IN" lub "OUT"
        )
        return {
            "message": "Stock updated successfully", 
            "new_quantity": updated_product.stock_quantity
        }
    except Exception as e:
        # Return error details if stock adjustment fails
        raise HTTPException(status_code=400, detail=str(e))

# ----------------------------------------------------------------------------------
#                                  REPORTS
# ----------------------------------------------------------------------------------

# -- ADMIN --
# Generate comprehensive inventory report using DB cursors
@router.get("/reports/inventory", tags=["Inventory: Reports"])
async def get_full_report(admin: User = Depends(get_admin_user)):
    """
    Fetch full movement history using a database iterator (cursor) for memory efficiency.
    """
    report = []
    # Stream entries via the service layer iterator
    async for entry in WarehouseService.get_inventory_report():
        report.append({
            "date": entry.created_at,
            "user": entry.user.login,
            "product": entry.product.name,
            "change": entry.quantity_change,
            "type": entry.action_type
        })
    return report

# Generate financial stock valuation grouped by supplier via raw SQL
@router.get("/reports/valuation", tags=["Inventory: Reports"])
async def get_valuation_report(admin: User = Depends(get_admin_user)):
    """
    Advanced Requirement: Complex SQL Query.
    Returns a financial valuation report grouped by supplier.
    Only accessible by administrators.
    """
    try:
        # Call the complex SQL query from the service layer
        report_data = await WarehouseService.get_supplier_valuation_report()
        
        return {
            "report_name": "Supplier Stock Valuation",
            "generated_at": datetime.now(),
            "currency": "PLN",
            "data": report_data
        }
    except Exception as e:
        # Handle potential SQL errors or connection issues
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating valuation report: {str(e)}"
        )

# ----------------------------------------------------------------------------------
#                                 SUPPLIERS
# ----------------------------------------------------------------------------------

# -- ADMIN --
@router.post("/suppliers", response_model=SupplierResponse, status_code=201, tags=["Inventory: Suppliers"])
async def create_supplier(data: SupplierCreate, admin: User = Depends(get_admin_user)):
    """Add a new supplier to the system."""
    return await Supplier.create(**data.model_dump())

# -- USER --
@router.get("/suppliers", response_model=list[SupplierResponse], tags=["Inventory: Suppliers"])
async def list_suppliers(current_user: User = Depends(get_current_user)):
    """List all suppliers (Available to all logged-in users)."""
    return await Supplier.all()

# ----------------------------------------------------------------------------------
#                                 LOCATIONS
# ----------------------------------------------------------------------------------

# -- ADMIN --
@router.post("/locations", response_model=LocationResponse, status_code=201, tags=["Inventory: Locations"])
async def create_location(data: LocationCreate, admin: User = Depends(get_admin_user)):
    """Define a new warehouse slot (Zone + Shelf)."""
    # Check if this zone and shelf combination is already taken
    existing = await Location.get_or_none(zone_name=data.zone_name, shelf_number=data.shelf_number)
    if existing:
        raise HTTPException(status_code=400, detail="Location already exists")
    
    # Create the location record
    return await Location.create(**data.model_dump())

# -- USER --
@router.get("/locations", response_model=list[LocationResponse], tags=["Inventory: Locations"])
async def list_locations(user: User = Depends(get_current_user)):
    """Returns a list of all warehouse locations."""
    return await Location.all()

# ----------------------------------------------------------------------------------
#                                 PRODUCTS
# ----------------------------------------------------------------------------------

# -- ADMIN --
@router.post("/products", response_model=ProductResponse, status_code=201, tags=["Inventory: Products"])
async def create_product(data: ProductCreate, admin: User = Depends(get_admin_user)):
    """Create a product and link it to a supplier and location."""
    if not await Supplier.exists(id=data.supplier_id):
        raise HTTPException(status_code=404, detail="Supplier not found")
    if not await Location.exists(id=data.location_id):
        raise HTTPException(status_code=404, detail="Location not found")
    
    product = await Product.create(**data.model_dump())

    # 🔑 fetch related so response_model can serialize correctly
    await product.fetch_related("supplier", "location")
    return product

@router.patch("/products/{product_id}", tags=["Inventory: Products"])
async def update_product_details(
    product_id: int, 
    data: ProductUpdate,
    admin: User = Depends(get_admin_user)
):
    product = await Product.get_or_none(id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = data.model_dump(exclude_unset=True)

    if "sku" in update_data:
        new_sku = update_data["sku"]
        if new_sku != product.sku and await Product.exists(sku=new_sku):
            raise HTTPException(status_code=400, detail="SKU already in use")
        product.sku = new_sku

    if "supplier_id" in update_data:
        if not await Supplier.exists(id=update_data["supplier_id"]):
            raise HTTPException(status_code=404, detail="Supplier not found")
        product.supplier_id = update_data["supplier_id"]

    if "location_id" in update_data:
        if not await Location.exists(id=update_data["location_id"]):
            raise HTTPException(status_code=404, detail="Location not found")
        product.location_id = update_data["location_id"]

    if "name" in update_data:
        product.name = update_data["name"]
    if "price" in update_data:
        product.price = update_data["price"]
        
    await product.save()
    return product

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Inventory: Products"])
async def delete_product(
    product_id: int, 
    admin: User = Depends(get_admin_user)
):
    """
    Administrative removal: Only admins can delete products from the database.
    This will also remove associated logs due to CASCADE constraints.
    """
    product = await Product.get_or_none(id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await product.delete()
    
    # Return a empty response not a dict
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# -- USER --
@router.get("/products", response_model=list[ProductResponse], tags=["Inventory: Products"])
async def list_products(user: User = Depends(get_current_user)):
    """
    Returns a list of products with nested supplier and location data.
    FastAPI handles the dictionary conversion automatically.
    """
    return await Product.all().prefetch_related("supplier", "location")
