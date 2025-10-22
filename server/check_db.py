import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Check remainders table structure
try:
    cursor.execute("PRAGMA table_info(remainders);")
    columns = cursor.fetchall()
    print("Remainders columns:", columns)
except Exception as e:
    print("Error checking remainders:", e)

# Check reminders table structure (if exists)
try:
    cursor.execute("PRAGMA table_info(reminders);")
    columns = cursor.fetchall()
    print("Reminders columns:", columns)
except Exception as e:
    print("Error checking reminders:", e)

conn.close()
