from tortoise import fields, models

class Supplier(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100, unique=True)
    contact_email = fields.CharField(max_length=100, null=True)

    class Meta:
        table = "suppliers"

class Location(models.Model):
    id = fields.IntField(primary_key=True)
    zone_name = fields.CharField(max_length=10)
    shelf_number = fields.IntField()
    
    class Meta:
        table = "locations"
        unique_together = (("zone_name", "shelf_number"),)

class Product(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100)
    sku = fields.CharField(max_length=50, unique=True)
    price = fields.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock_quantity = fields.IntField(default=0)
    
    # Relationships
    supplier = fields.ForeignKeyField("models.Supplier", related_name="products", null=True)
    location = fields.ForeignKeyField("models.Location", related_name="products", null=True)

    class Meta:
        table = "products"

class WarehouseLog(models.Model):
    id = fields.IntField(primary_key=True)
    action_type = fields.CharField(max_length=20)
    quantity_change = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)

    # Note: Tortoise will resolve "models.User" from the user app
    user = fields.ForeignKeyField("models.User", related_name="logs")
    product = fields.ForeignKeyField("models.Product", related_name="logs")

    class Meta:
        table = "warehouse_logs"
