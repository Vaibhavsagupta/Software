import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data.db')
if not os.path.exists(db_path):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.db')

def update_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tables to update with new columns
    tables_to_check = {
        "orders": [
            ("patient_name", "VARCHAR"),
            ("products", "VARCHAR"),
            ("model_number", "VARCHAR"),
            ("order_amount", "FLOAT DEFAULT 0.0"),
            ("warranty_expiry", "DATETIME")
        ],
        "invoices": [
            ("due_date", "DATETIME")
        ],
        "payments": [
            ("applied_amount", "FLOAT DEFAULT 0.0"),
            ("status", "VARCHAR DEFAULT 'active'")
        ],
        "adjustments": [
            ("adj_type", "VARCHAR DEFAULT 'Discount'"),
            ("applied_to_invoice_id", "INTEGER")
        ]
    }

    for table, columns in tables_to_check.items():
        for col_name, col_type in columns:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
                print(f"Added column {col_name} to {table}")
            except sqlite3.OperationalError:
                pass

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_db()
