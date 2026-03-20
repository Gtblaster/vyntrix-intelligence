import sqlite3

DB_PATH = "contacts.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if table exists
    try:
        c.execute("SELECT id, name, email, message, timestamp FROM contacts")
        rows = c.fetchall()
        
        print(f"--- VYNTRIX CONTACTS DATABASE ---")
        print(f"Total Transmissions: {len(rows)}")
        print("-" * 50)
        
        for row in rows:
            print(f"ID: {row[0]}")
            print(f"Name: {row[1]}")
            print(f"Email: {row[2]}")
            print(f"Message: {row[3]}")
            print(f"Time: {row[4]}")
            print("-" * 50)
            
    except sqlite3.OperationalError:
        print("Database or table does not exist yet. Try submitting the contact form first.")
        
    conn.close()

if __name__ == "__main__":
    main()
