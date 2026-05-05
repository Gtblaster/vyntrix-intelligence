import os

DB_PATH = "contacts.db"

def main():
    if not os.path.exists(DB_PATH):
        print("Database does not exist yet. Try submitting the contact form first.")
        return
        
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            
        print(f"--- VYNTRIX CONTACTS DATABASE ---")
        print(f"Total Transmissions: {len(lines)}")
        print("-" * 50)
        
        for i, line in enumerate(lines, 1):
            line = line.encode('ascii', errors='replace').decode('ascii')
            if line.startswith("["):
                try:
                    time_end = line.index("]")
                    time_str = line[1:time_end]
                    rest = line[time_end+2:]
                    parts = rest.split(" | ")
                    name_part = parts[0].replace("Name: ", "").strip()
                    email_part = parts[1].replace("Email: ", "").strip()
                    msg_part = parts[2].replace("Message: ", "").strip()
                    
                    print(f"ID: {i}")
                    print(f"Name: {name_part}")
                    print(f"Email: {email_part}")
                    print(f"Message: {msg_part}")
                    print(f"Time: {time_str}")
                except Exception:
                    print(f"Raw Entry {i}: {line}")
            else:
                print(f"Raw Entry {i}: {line}")
                
            print("-" * 50)
            
    except Exception as e:
        print(f"Error reading database: {e}")

if __name__ == "__main__":
    main()
