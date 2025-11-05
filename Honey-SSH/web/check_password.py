import sqlite3

conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute('SELECT email, password_hash FROM users')
rows = cur.fetchall()

print("Database Users:")
print("-" * 80)
for email, hash_value in rows:
    print(f"Email: {email}")
    print(f"Password Hash: {hash_value[:60]}...")
    print("-" * 80)

conn.close()
