# routes/analyzers/results.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from shared.file_queue import load_analysis
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates") 

@router.get("/result/{analysis_id}")
async def show_result(analysis_id: str, request: Request):
    """Show analysis results"""
    print(f"🎯 RESULT ROUTE HIT for {analysis_id}")
    
    data = load_analysis(analysis_id)
    
    if not data:
        return HTMLResponse("Result not found")
    
    if data.get("status") != "complete":
        return templates.TemplateResponse("loading.html", {
            "request": request,
            "analysis_id": analysis_id
        })
    
    # Get the current date for display
    from datetime import datetime
    analysis_date = datetime.now().strftime("%B %d, %Y")
    
    return templates.TemplateResponse("result.html", {
        "request": request,
        "result_text": data.get("result", "No result available"),
        "analysis_type": data.get("feature", "Code Analysis").title(),
        "analysis_date": analysis_date
    })
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Result</title>
    <style>
        body {{ background: #0f172a; color: white; font-family: sans-serif; padding: 2rem; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .result-wrapper {{ position: relative; margin-bottom: 2rem; }}
        pre {{
            background: #1e293b;
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 70vh;
            border: 1px solid #334155;
            font-family: 'SF Mono', Monaco, Consolas, monospace;
            font-size: 14px;
            line-height: 1.5;
        }}
        .copy-btn {{
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: #0cc0df;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.2s ease;
            z-index: 10;
        }}
        .copy-btn:hover {{ background: #0aa8c4; }}
        .back-link {{ color: #0cc0df; text-decoration: none; display: inline-block; margin-top: 1rem; }}
        .back-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1 style="color:#0cc0df;">Analysis Complete</h1>
        
        <div class="result-wrapper">
            <pre id="result-text">{result}</pre>
            <button class="copy-btn" onclick="copyToClipboard()">
                 Copy
            </button>
        </div>
        
        <a href="/analyze/snippet" class="back-link">← Analyze Another Snippet</a>
    </div>

    <script>
    function copyToClipboard() {{
        const text = document.getElementById('result-text').innerText;
        navigator.clipboard.writeText(text).then(() => {{
            const btn = document.querySelector('.copy-btn');
            const originalText = btn.innerHTML;
            btn.innerHTML = 'Copied!';
            setTimeout(() => {{
                btn.innerHTML = originalText;
            }}, 2000);
        }}).catch(err => {{
            alert('Failed to copy text: ' + err);
        }});
    }}
    </script>
</body>
</html>
"""
    return HTMLResponse(html)