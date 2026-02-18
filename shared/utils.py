# shared/utils.py
from fastapi.responses import HTMLResponse

async def loading_response(analysis_id: str):
    """Return loading page for analysis jobs"""
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Analyzing...</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link rel="stylesheet" href="/static/css/brand.css">
        <meta http-equiv="refresh" content="5">
        <style>
            body {{
                background: #0f172a;
                color: white;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                margin: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .loading-container {{
                text-align: center;
                padding: 2rem;
            }}
            .icon {{
                font-size: 4rem;
                color: #fbbf24;
                margin-bottom: 1rem;
            }}
            h1 {{
                color: white;
                margin-bottom: 1rem;
            }}
            .progress-bar {{
                width: 300px;
                height: 6px;
                background: #1e293b;
                border-radius: 3px;
                margin: 2rem auto;
                overflow: hidden;
            }}
            .progress-fill {{
                height: 100%;
                background: #0cc0df;
                width: 30%;
                border-radius: 3px;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0% {{ opacity: 0.6; width: 30%; }}
                50% {{ opacity: 1; width: 70%; }}
                100% {{ opacity: 0.6; width: 30%; }}
            }}
        </style>
    </head>
    <body>
        <div class="loading-container">
            <div class="icon">
                <i class="fas fa-lightbulb"></i>
            </div>
            <h1>Analyzing your code</h1>
            <p>This will take 30-60 seconds</p>
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <p style="color: #94a3b8; margin-top: 1rem;">This page refreshes automatically</p>
        </div>
    </body>
    </html>
    '''
    return HTMLResponse(html)