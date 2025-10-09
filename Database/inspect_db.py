import os
import sqlite3
import csv
import argparse

DB = os.path.join(os.path.dirname(__file__), 'users.db')

def list_users():
    if not os.path.exists(DB):
        print("Database not found:", DB)
        return []
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, email, created_at FROM users ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows

def export_csv(path):
    rows = list_users()
    if not rows:
        print("No rows to export.")
        return
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id', 'email', 'created_at'])
        w.writerows(rows)
    print("Exported", len(rows), "rows to", path)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', help='Export user list to CSV file')
    args = p.parse_args()
    rows = list_users()
    if not rows:
        print("No users found.")
    else:
        print(f"Found {len(rows)} user(s):")
        for r in rows:
            print(f"  id={r[0]}  email={r[1]}  created_at={r[2]}")
    if args.csv:
        export_csv(args.csv)

if __name__ == '__main__':
    main()