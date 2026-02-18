# routes/analyzers/base.py
from shared.file_queue import save_analysis
import os
from openai import AsyncOpenAI
import asyncio

async def run_analysis(analysis_id: str, data: dict, prompt_template: str):
    """Single source of truth for all analysis"""
    try:
        print(f"🚀 Base analysis started for {analysis_id}")
        print(f"📦 Initial data keys: {list(data.keys())}")
        
        # Update progress
        data["progress"] = 0.3
        data["message"] = "Processing..."
        save_analysis(analysis_id, data)
        print(f"💾 Saved progress update")
        
        # Get API key
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        print(f"🔑 API key present: {'Yes' if api_key and not api_key.startswith('your-') else 'No'}")
        
        if not api_key or api_key.startswith("your-"):
            print(f"📝 Using mock response")
            result = f"""ANALYSIS COMPLETE (Mock Mode)

Feature: {data.get('feature', 'unknown')}
Level: {data.get('level', 'professional')}

This is a placeholder response. Add your DeepSeek API key to .env for real analysis."""
            data["is_mock"] = True
        else:
            # Real AI call
            print(f"🤖 Calling DeepSeek API...")
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            
            # Add formatting instruction
            full_prompt = prompt_template + "\n\nIMPORTANT: Use plain text only. No markdown symbols (#, *, -, `). Just plain sentences with line breaks."
            print(f"📝 Prompt length: {len(full_prompt)} chars")
            
            try:
                response = await asyncio.wait_for(
                    client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": "You are a helpful technical expert."},
                            {"role": "user", "content": full_prompt}
                        ],
                        max_tokens=1500,
                        temperature=0.3
                    ),
                    timeout=45.0
                )
                print(f"✅ AI responded successfully")
                result = response.choices[0].message.content
                data["is_mock"] = False
            except asyncio.TimeoutError:
                print(f"⏱️ AI call timed out")
                result = "Analysis timed out. Please try again."
                data["is_error"] = True
            except Exception as e:
                print(f"❌ AI call failed: {e}")
                raise
        
        # Store result
        print(f"💾 Saving final result")
        data["result"] = result
        data["status"] = "complete"
        data["progress"] = 1.0
        data["message"] = "Complete!"
        
        # Save to file queue
        save_analysis(analysis_id, data)
        print(f"✅ Base analysis complete for {analysis_id}")
        
    except Exception as e:
        print(f"❌ Error in base analysis: {e}")
        import traceback
        traceback.print_exc()
        data["status"] = "error"
        data["error"] = str(e)
        data["message"] = f"Error: {str(e)}"
        save_analysis(analysis_id, data)