from shared.file_queue import save_analysis
import os
from openai import AsyncOpenAI
import asyncio

async def run_analysis(analysis_id: str, data: dict, prompt_template: str):
    """Single source of truth for all analysis"""
    try:
        print(f"🚀 Base analysis started for {analysis_id}")
        
        data["progress"] = 0.3
        data["message"] = "Processing..."

        # ===== TOKEN DEDUCTION =====
        user_email = data.get("user_email")
        if user_email:
            from shared.auth import deduct_token
            deduct_token(user_email)
            print(f"💰 Deducted token for {user_email}")

        print(f"💰 TOKEN DEBUG: user_email={user_email}, deducted={user_email is not None}")

        save_analysis(analysis_id, data)
        
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        
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
            
            # Strong formatting instructions
            system_message = """You are a helpful technical expert. 
CRITICAL: Respond in PLAIN TEXT ONLY. 
- NO markdown symbols (#, *, -, `, >, [])
- NO asterisks for bold
- NO hash symbols for headers
- NO backticks for code
Just use plain sentences with line breaks between sections.
Explain code simply and clearly like you're talking to another developer."""
            
            # Add reminder to user prompt
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
