import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("database.db")  # creates database.db if it doesn't exist
c = conn.cursor()

# Create users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Create articles table
c.execute('''
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    url TEXT,
    label TEXT,
    confidence REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Insert demo users if they don't exist
demo_users = [
    ('demo', 'demo123'),
    ('admin', 'admin123'),
    ('test', 'test123')
]

for username, password in demo_users:
    hashed = generate_password_hash(password)
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        print(f"Inserted user (username: {username}, password: {password})")
    else:
        print(f"User '{username}' already exists")

conn.commit()
conn.close()
print("Database and tables created/verified successfully!")