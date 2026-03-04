import os
import asyncpg
from datetime import datetime

DB_PATH = os.getenv("DATABASE_URL")

async def get_db_connection(statement_cache_size=None):
    if statement_cache_size is not None:
        return await asyncpg.connect(DB_PATH, statement_cache_size=statement_cache_size)
    return await asyncpg.connect(DB_PATH)

async def store_magic_token(email: str, token: str) -> bool:
    """Store magic token in database."""
    print(f"💾 STORING TOKEN: {token} for {email}")
    
    try:
        conn = await get_db_connection()
        
        # Create table if not exists
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS magic_links (
                token TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                created TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE
            )
        ''')
        
        await conn.execute('''
            INSERT INTO magic_links (token, email, created, used)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (token) DO UPDATE SET
                email = $2,
                created = $3,
                used = $4
        ''', token, email, datetime.now(), False)
        
        await conn.close()
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

async def verify_magic_link(token: str, mark_used: bool = True):
    """Verify a magic link token"""
    print(f"🔍 VERIFYING TOKEN: {token}")
    
    try:
        conn = await get_db_connection()
        
        # Check if token exists
        result = await conn.fetchrow(
            "SELECT email FROM magic_links WHERE token = $1",
            token
        )
        
        if result:
            email = result['email']
            if mark_used:
                await conn.execute(
                    "UPDATE magic_links SET used = TRUE WHERE token = $1",
                    token
                )
            await conn.close()
            return email
        
        await conn.close()
        return None
        
    except Exception as e:
        print(f"❌ verify_magic_link error: {e}")
        return None

async def get_user_tokens(email: str) -> int:
    # Demo users get fake tokens
    if email.startswith("demo_"):
        return 5
    
    """Get user's remaining tokens, resetting monthly if needed."""
    conn = await get_db_connection()
    
    # Create users table if not exists
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            tokens INTEGER DEFAULT 5,
            last_token_reset TEXT
        )
    ''')
    
    # Get user's current tokens and last reset month
    result = await conn.fetchrow(
        "SELECT tokens, last_token_reset FROM users WHERE email = $1",
        email
    )
    
    current_month = datetime.now().strftime('%Y-%m')
    
    if not result:
        # New user: give 5 tokens
        await conn.execute('''
            INSERT INTO users (email, tokens, last_token_reset)
            VALUES ($1, $2, $3)
        ''', email, 5, current_month)
        await conn.close()
        return 5
    
    tokens, last_reset_month = result['tokens'], result['last_token_reset']
    
    # If the month has changed, reset tokens
    if last_reset_month != current_month:
        tokens = 5
        await conn.execute('''
            UPDATE users SET tokens = $1, last_token_reset = $2 WHERE email = $3
        ''', tokens, current_month, email)
        print(f"🔄 Reset tokens for {email} to 5 for new month {current_month}")
    
    await conn.close()
    return tokens

async def deduct_token(email: str) -> bool:
    """Deduct one token from user's balance"""
    try:
        conn = await get_db_connection()
        
        # Ensure user exists
        current_month = datetime.now().strftime('%Y-%m')
        await conn.execute('''
            INSERT INTO users (email, tokens, last_token_reset)
            VALUES ($1, $2, $3)
            ON CONFLICT (email) DO NOTHING
        ''', email, 5, current_month)
        
        # Deduct token
        result = await conn.execute('''
            UPDATE users SET tokens = tokens - 1
            WHERE email = $1 AND tokens > 0
        ''', email)
        
        await conn.close()
        
        success = result == "UPDATE 1"
        if success:
            print(f"✅ Deducted token for {email}")
        else:
            print(f"⚠️ No tokens to deduct for {email}")
        
        return success
        
    except Exception as e:
        print(f"❌ deduct_token error: {e}")
        return False

async def send_magic_link(email: str, token: str):
    user_agent = request.headers.get('User-Agent', 'unknown')
    print(f"📱 Mobile? {'iOS' if 'iPhone' in user_agent else 'Android' if 'Android' in user_agent else 'Desktop'} - {email}")
    

    """Send magic link email via Resend"""
    magic_link = f"https://codedecipher.app/auth?token={token}"
    
    print(f"🔗 Magic link for {email}: https://codedecipher.app/auth?token={token}")

    try:
        import resend
        resend.api_key = os.getenv("RESEND_API_KEY")
        
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