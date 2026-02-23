# shared/auth.py

import os
import json
import resend
import sqlite3

from datetime import datetime
from dotenv import load_dotenv

env_path = '/root/codedecipher/.env'
load_dotenv()

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bank.db')
print(f"📂 Using database at: {DB_PATH}")

# Debug prints
print(f"📂 Loading .env from: {env_path}")
print(f"🔑 RESEND_API_KEY exists: {bool(os.getenv('RESEND_API_KEY'))}")
if os.getenv('RESEND_API_KEY'):
    print(f"🔑 Key starts with: {os.getenv('RESEND_API_KEY')[:10]}...")

resend.api_key = os.getenv("RESEND_API_KEY")

def send_magic_link(email: str, token: str):
    print(f"🔑 Resend key in auth.py: {os.getenv('RESEND_API_KEY', 'NOT FOUND')[:10]}...")
    """Send magic link email via Resend"""
    magic_link = f"https://codedecipher.app/auth?token={token}"
    
    try:
        params = {
            "from": "noreply@codedecipher.app",
            "to": [email],
            "subject": "Your CodeDecipher Login Link",
            "html": f"""
                <h2>Login to CodeDecipher</h2>
                <p>Click the link below to log in:</p>
                <p><a href="{magic_link}">{magic_link}</a></p>
                <p>This link expires in 24 hours.</p>
                <p>If you didn't request this, ignore this email.</p>
            """
        }
        
        result = resend.Emails.send(params)
        print(f"✅ Magic link email sent to {email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def store_magic_token(email: str, token: str) -> bool:
    print(f"💾 STORING TOKEN: {token} for {email}")
    
    try:
        conn = sqlite3.connect(DB_PATH)  # ← CHANGE HERE
        cursor = conn.cursor()
        
        # Debug: show what's in DB before insert
        cursor.execute("SELECT token, email FROM magic_links")
        existing = cursor.fetchall()
        print(f"💾 Existing tokens in DB: {existing}")
        
        cursor.execute("""
            INSERT OR REPLACE INTO magic_links (token, email, created, used)
            VALUES (?, ?, ?, ?)
        """, (token, email, datetime.now(), False))
        
        conn.commit()
        conn.close()
        print(f"✅ Token stored for: {email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to store token: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_magic_link(email: str) -> str:
    """Create a unique token for magic link."""
    import uuid
    token = f"magic_{uuid.uuid4().hex}"
    return token

def verify_magic_link(token: str, mark_used: bool = True):
    print(f"🔍 VERIFYING TOKEN: {token}")
    print(f"📂 DB Path: {DB_PATH}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # DUMP THE ENTIRE TABLE
        cursor.execute("SELECT token, email, used, created FROM magic_links")
        all_rows = cursor.fetchall()
        print(f"📊 ALL TOKENS IN DB: {all_rows}")
        
        # Check if our token exists
        cursor.execute("SELECT email FROM magic_links WHERE token = ?", (token,))
        result = cursor.fetchone()
        print(f"🔍 Token lookup result: {result}")
        
        if result:
            email = result[0]
            if mark_used:
                cursor.execute("UPDATE magic_links SET used = 1 WHERE token = ?", (token,))
                conn.commit()
            conn.close()
            return email
        
        conn.close()
        return None
    except Exception as e:
        print(f"❌ verify_magic_link error: {e}")
        return None
    
# Token management functions
def get_user_tokens(email: str) -> int:
    """Get user's remaining tokens"""
    # This would query your user database
    # For now, using the same storage as magic links
    user_data = get_user_data(email)  # You'll need to create this
    return user_data.get("tokens", 5)

def deduct_token(email: str) -> bool:
    """Deduct one token from user's balance"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Ensure user exists
        cursor.execute(
            "INSERT OR IGNORE INTO users (email, tokens, last_token_reset) VALUES (?, 5, datetime('now'))",
            (email,)
        )
        
        # Deduct token
        cursor.execute(
            "UPDATE users SET tokens = tokens - 1 WHERE email = ? AND tokens > 0",
            (email,)
        )
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        if success:
            print(f"✅ Deducted token for {email}")
        else:
            print(f"⚠️ No tokens to deduct for {email}")
        
        return success
    except Exception as e:
        print(f"❌ deduct_token error: {e}")
        return False

def reset_monthly_tokens(email: str):
    """Reset user's tokens to monthly allowance"""
    user_data = get_user_data(email)
    last_reset = user_data.get("last_token_reset")
    
    if not last_reset or datetime.now() - datetime.fromisoformat(last_reset) > timedelta(days=30):
        user_data["tokens"] = 5
        user_data["last_token_reset"] = datetime.now().isoformat()
        save_user_data(email, user_data)

def get_user_tokens(email: str) -> int:
    """Get user's remaining tokens"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                tokens INTEGER DEFAULT 5,
                last_token_reset TIMESTAMP
            )
        ''')
        
        # Get or create user
        cursor.execute("SELECT tokens FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        
        if result:
            tokens = result[0]
        else:
            tokens = 5
            cursor.execute(
                "INSERT INTO users (email, tokens, last_token_reset) VALUES (?, ?, ?)",
                (email, tokens, datetime.now())
            )
            conn.commit()
        
        conn.close()
        return tokens
    except Exception as e:
        print(f"❌ Error getting tokens: {e}")
        return 5  # Default fallback
