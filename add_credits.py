import sqlite3
import sys

def add_tokens(email, tokens):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    
    # Update or insert user
    cursor.execute('''
        INSERT INTO users (email, tokens, last_token_reset)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT(email) DO UPDATE SET tokens = tokens + ?
    ''', (email, tokens, tokens))
    
    conn.commit()
    conn.close()
    print(f"✅ Added {tokens} tokens to {email}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_credits.py email@example.com 5")
    else:
        add_tokens(sys.argv[1], int(sys.argv[2]))