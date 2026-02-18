# shared/prompts.py

GITHUB_PROMPT = """Analyze this GitHub repository for a {level} audience.

Repository: {repo_url}
Branch: {branch}
Files analyzed: {file_count} key files

Please provide:
1. PROJECT OVERVIEW: What does this codebase do?
2. TECH STACK: Languages, frameworks, key dependencies
3. ARCHITECTURE: Main components and how they connect
4. COMPLEXITY: Areas that need attention
5. ONBOARDING: What a new developer needs to know

{specific_questions}

FILE SAMPLES:
{file_context}

IMPORTANT: Use plain text only. No markdown symbols (#, *, -, `). Just plain sentences with line breaks between sections.
Keep analysis under 800 words.

"IMPORTANT: Provide a complete analysis. Do not truncate or cut off mid-sentence.""""

SECURITY_PROMPT = """Perform a security review of this code for a {level} audience.

Please provide:
1. VULNERABILITIES: Specific security issues found
2. INPUT VALIDATION: How user input is handled
3. AUTH/PERMISSIONS: Access control concerns
4. SECURE CODING: Best practices to implement
5. PRIORITY: What to fix immediately

{content}

IMPORTANT: Use plain text only. No markdown symbols (#, *, -, `). Just plain sentences with line breaks between sections.
"IMPORTANT: Provide a complete analysis. Do not truncate or cut off mid-sentence.""""

SNIPPET_PROMPT = """Analyze this code for a {level} audience.

Please provide:
1. PURPOSE: What does this code do?
2. LOGIC: Key operations and flow
3. COMPLEXITY: Areas that might be hard to maintain
4. EDGE CASES: Missing error handling or assumptions
5. IMPROVEMENTS: How to make it better

{content}

IMPORTANT: Use plain text only. No markdown symbols (#, *, -, `). Just plain sentences with line breaks between sections.
"IMPORTANT: Provide a complete analysis. Do not truncate or cut off mid-sentence.""""

API_PROMPT = """Analyze this API documentation/code for a {level} audience.

Please provide:
1. PURPOSE: What does this API do?
2. ENDPOINTS: Key operations and their purpose
3. AUTH: How authentication works
4. DATA FORMATS: Request/response structure
5. USAGE: Common implementation patterns

{content}

IMPORTANT: Use plain text only. No markdown symbols (#, *, -, `). Just plain sentences with line breaks between sections.
"IMPORTANT: Provide a complete analysis. Do not truncate or cut off mid-sentence.""""