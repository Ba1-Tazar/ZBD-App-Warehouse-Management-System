from tortoise import Tortoise
from tortoise.transactions import in_transaction
from .model import Product, WarehouseLog
from user.model import User

class WarehouseService:

    staticmethod
    async def adjust_stock(product_id: int, user: User, amount: int, action: str):
        """
        Handles stock level updates and logging within a single atomic transaction.
        The using_db(conn) calls ensure all operations stay within the transaction context.
        """
        async with in_transaction() as conn:
            # Fetch product instance using the active transaction connection
            product = await Product.get(id=product_id).using_db(conn)
            
            # Update quantity based on action type
            if action.upper() == "OUT":
                if product.stock_quantity < amount:
                    raise Exception("Not enough stock available")
                product.stock_quantity -= amount
            else:
                product.stock_quantity += amount

            # Persist changes to the product table
            await product.save(using_db=conn)
            
            # Create an audit log entry linked to the user and product
            await WarehouseLog.create(
                action_type=action.upper(),
                quantity_change=amount if action.upper() == "IN" else -amount,
                product=product,
                user=user,
                using_db=conn
            )
            return product

    @staticmethod
    async def get_inventory_report():
        """
        Asynchronous generator that streams log entries using a database cursor.
        The .iterate() method prevents loading all records into memory at once.
        """
        async for log in WarehouseLog.all().prefetch_related("product", "user").iterate():
            yield log

    @staticmethod
    async def get_supplier_valuation_report():
        """
        Executes a raw SQL query to perform server-side data aggregation.
        Calculates total stock value by joining products and suppliers with GROUP BY.
        """
        connection = Tortoise.get_connection("default")
        
        sql_query = """
            SELECT s.name AS supplier_name, 
                   COUNT(p.id) AS unique_products, 
                   SUM(p.stock_quantity) AS total_units,
                   SUM(p.price * p.stock_quantity) AS total_valuation
            FROM suppliers s
            LEFT JOIN products p ON s.id = p.supplier_id
            GROUP BY s.name
            HAVING SUM(p.stock_quantity) > 0
            ORDER BY total_valuation DESC
        """
        
        # Returns raw query results as a list of dictionaries
        return await connection.execute_query_dict(sql_query)
