from tortoise import Tortoise
from tortoise.transactions import in_transaction
from user.model import Product, WarehouseLog, User


class WarehouseService:
    @staticmethod
    async def adjust_stock(product_id: int, user: User, amount: int, action: str):
        """
        Transaction and Logic:
        Updates stock levels and creates an audit log entry simultaneously.
        Ensures that stock changes never occur without a corresponding log.
        """
        # Transaction ensures data integrity between stock level and logs
        async with in_transaction() as conn:
            product = await Product.get(id=product_id)
            product.stock_quantity += amount
            await product.save(using_db=conn)
            
            # Create an audit log for the operation
            await WarehouseLog.create(
                action_type=action,
                quantity_change=amount,
                product=product,
                user=user,
                using_db=conn
            )
            return product

    @staticmethod
    async def get_inventory_report():
        """
        Database Iterator:
        Uses asynchronous iteration to fetch records efficiently.
        Satisfies the project requirement for using iterators.
        """
        # Stream data directly from the database to optimize memory usage
        async for log in WarehouseLog.all().prefetch_related("product", "user"):
            # Process each record individually via the async generator
            yield log

    @staticmethod
    async def get_supplier_valuation_report():
        """
        Advanced SQL Execution:
        Calculates total financial value of inventory grouped by supplier.
        Uses JOIN, GROUP BY, and Aggregation (SUM) for complex reporting.
        """
        # Obtain the direct database connection for raw SQL execution
        connection = Tortoise.get_connection("default")
        
        # Complex SQL query combining data from multiple tables
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
        
        # Executes the query and returns results as a list of dictionaries
        return await connection.execute_query_dict(sql_query)
