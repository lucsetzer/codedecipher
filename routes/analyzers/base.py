from shared.file_queue import save_analysis
import os
from openai import AsyncOpenAI
import asyncio
import asyncpg
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

async def log_analysis(analysis_id: str, data: dict):
    """Log analysis to PostgreSQL"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Create table if not exists
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                user_email TEXT NOT NULL,
                feature TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                tokens_used INTEGER DEFAULT 1
            )
        ''')
        
        user_email = data.get("user_email")
        if user_email:
            await conn.execute('''
                INSERT INTO analyses (id, user_email, feature, timestamp)
                VALUES ($1, $2, $3, $4)
            ''', analysis_id, user_email, data.get('feature'), datetime.now())
            print(f"📊 Logged {data.get('feature')} analysis for {user_email}")
        
        await conn.close()
    except Exception as e:
        print(f"❌ Failed to log analysis: {e}")

async def run_analysis(analysis_id: str, data: dict, prompt_template: str):
    """Single source of truth for all analysis"""
    try:
        print(f"🚀 Base analysis started for {analysis_id}")
        
        data["progress"] = 0.3
        data["message"] = "Processing..."
        save_analysis(analysis_id, data)
        
        api_key = os.getenv("DEEPSEEK_API_KEY", "")

        print("✅ DeepSeek response received")
        
        if not api_key or api_key.startswith("your-"):
            result = f"""ANALYSIS COMPLETE (Mock Mode)

Feature: {data.get('feature', 'unknown')}
Level: {data.get('level', 'professional')}

This is a placeholder response. Add your DeepSeek API key to .env for real analysis."""
            data["is_mock"] = True
        else:
            client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            
            system_message = """You are a helpful technical expert. 
CRITICAL: Respond in PLAIN TEXT ONLY. 
- NO markdown symbols (#, *, -, `, >, [])
- NO asterisks for bold
- NO hash symbols for headers
- NO backticks for code
Just use plain sentences with line breaks between sections.
Explain code simply and clearly like you're talking to another developer."""
            
            full_prompt = prompt_template + "\n\nRemember: PLAIN TEXT ONLY. No symbols or formatting."
            
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": full_prompt}
                    ],
                    max_tokens=1500,
                    temperature=0.3
                ),
                timeout=45.0
            )
            
            result = response.choices[0].message.content
            data["is_mock"] = False
        
        data["result"] = result
        data["status"] = "complete"
        data["progress"] = 1.0
        data["message"] = "Complete!"
        
        # ===== TOKEN DEDUCTION =====
        user_email = data.get("user_email")
        if user_email:
            from shared.auth import deduct_token
            await deduct_token(user_email)
            print(f"💰 Deducted token for {user_email}")
            
            # Log analysis to PostgreSQL
            await log_analysis(analysis_id, data)
        
        save_analysis(analysis_id, data)
        print(f"✅ Base analysis complete for {analysis_id}")
        
    except Exception as e:
        print(f"❌ Error in base analysis: {e}")
        data["status"] = "error"
        data["error"] = str(e)
        data["message"] = f"Error: {str(e)}"
        save_analysis(analysis_id, data)
        import traceback
        traceback.print_exc()