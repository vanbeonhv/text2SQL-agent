"""Initialize databases."""
import asyncio
import json
from .history import history_manager
from .connection import history_db, target_db
from ..config import settings


async def init_history_db():
    """Initialize history database schema."""
    print("Initializing history database...")
    await history_manager.reset_database()
    print(f"✓ History database initialized at {settings.history_db_path}")


async def init_target_db():
    """Initialize target database with example data."""
    print("Initializing target database with example data...")
    
    # Create products table
    await target_db.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT,
            stock INTEGER DEFAULT 0
        )
    """)
    
    # Create orders table
    await target_db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            customer_name TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    
    # Insert example products
    products = [
        (1, "Laptop", 999.99, "Electronics", 15),
        (2, "Mouse", 29.99, "Electronics", 50),
        (3, "Keyboard", 79.99, "Electronics", 30),
        (4, "Monitor", 299.99, "Electronics", 20),
        (5, "Desk Chair", 199.99, "Furniture", 10),
    ]
    
    for product in products:
        await target_db.execute(
            "INSERT OR IGNORE INTO products (id, name, price, category, stock) VALUES (?, ?, ?, ?, ?)",
            product
        )
    
    # Insert example orders
    orders = [
        (1, 1, 2, "2024-01-15", "John Doe"),
        (2, 2, 5, "2024-01-16", "Jane Smith"),
        (3, 1, 1, "2024-01-17", "Bob Johnson"),
    ]
    
    for order in orders:
        await target_db.execute(
            "INSERT OR IGNORE INTO orders (id, product_id, quantity, order_date, customer_name) VALUES (?, ?, ?, ?, ?)",
            order
        )
    
    print(f"✓ Target database initialized at {settings.target_db_path}")


async def create_example_schema():
    """Create example schema.json file."""
    schema = {
        "tables": [
            {
                "name": "products",
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "name", "type": "TEXT"},
                    {"name": "price", "type": "REAL"},
                    {"name": "category", "type": "TEXT"},
                    {"name": "stock", "type": "INTEGER"}
                ]
            },
            {
                "name": "orders",
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "product_id", "type": "INTEGER"},
                    {"name": "quantity", "type": "INTEGER"},
                    {"name": "order_date", "type": "TIMESTAMP"},
                    {"name": "customer_name", "type": "TEXT"}
                ]
            }
        ],
        "relationships": [
            {
                "from": "orders.product_id",
                "to": "products.id",
                "type": "foreign_key"
            }
        ]
    }
    
    with open(settings.schema_path, 'w') as f:
        json.dump(schema, f, indent=2)
    
    print(f"✓ Schema file created at {settings.schema_path}")


async def main():
    """Initialize all databases."""
    print("Starting database initialization...\n")
    
    try:
        await init_history_db()
        await init_target_db()
        await create_example_schema()
        
        print("\n✅ All databases initialized successfully!")
        print(f"\nYou can now run the server with:")
        print(f"  uvicorn app.main:app --reload")
    finally:
        await history_db.close()
        await target_db.close()


if __name__ == "__main__":
    asyncio.run(main())
