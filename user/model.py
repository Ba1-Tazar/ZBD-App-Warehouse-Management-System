from tortoise import fields, models

class User(models.Model):
    """
    Tortoise ORM model defining the 'users' table in PostgreSQL.
    """
    id = fields.IntField(primary_key=True)
    login = fields.CharField(max_length=100, unique=True)
    password = fields.CharField(max_length=255)
    is_admin = fields.BooleanField(default=False)

    class Meta:
        table = "users"
