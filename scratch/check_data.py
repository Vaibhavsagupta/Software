import sqlite3

def check_db():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    tables = ['invoices', 'orders', 'payments', 'shipments', 'clients']
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"Table {table}: {count} records")
        except Exception as e:
            print(f"Error checking {table}: {e}")
    conn.close()

if __name__ == "__main__":
    check_db()
