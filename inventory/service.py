from user.model import Product, WarehouseLog, User
from tortoise.transactions import in_transaction

class WarehouseService:
    @staticmethod
    async def adjust_stock(product_id: int, user: User, amount: int, action: str):
        """
        Example of a Transaction and Logic:
        Updates stock and creates a log entry simultaneously.
        """
        async with in_transaction() as conn:
            product = await Product.get(id=product_id)
            product.stock_quantity += amount
            await product.save(using_db=conn)

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
        Example of an Iterator:
        Useful for processing large datasets without crashing memory.
        """
        # .all().iterate() returns a cursor/iterator
        async for log in WarehouseLog.all().prefetch_related("product", "user").iterate():
            # You can process logs one by one here
            yield log
