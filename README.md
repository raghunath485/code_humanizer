# Code Humanizer V2

Code Humanizer V2 is an AI-oriented code transformation platform focused on readability, conversion, analysis, and developer storytelling.

## Included workflows

- Humanize code with identifier expansion, language detection, complexity analysis, dead-code detection, and walkthroughs
- Convert code between C, C++, Java, and Python with confidence scores and warnings
- Apply concept preferences such as functions, loops, OOP, async programming, and API usage
- Score readability, maintainability, complexity, security, and overall humanization quality
- Detect risky patterns including `eval`, `exec`, SQL injection hints, hardcoded secrets, unsafe deserialization, and command injection
- Generate project summaries, resume bullet points, technical highlights, and interview preparation material

## Architecture

- `app_backend/main.py`: FastAPI app and API routes
- `app_backend/humanizer_engine.py`: humanization, walkthroughs, quality, and security integration
- `app_backend/converter_engine.py`: multi-language conversion pipeline
- `app_backend/concept_engine.py`: concept rules engine and refactor-mode guidance
- `app_backend/security_engine.py`: heuristic security scanning
- `app_backend/career_engine.py`: resume and interview assistant output
- `services.js` and `components.js`: frontend service and rendering layers

## Run locally

1. Install dependencies:

```bash
py -3 -m pip install -r requirements.txt
```

2. Start the app:

```bash
py -3 server.py
```

3. Open `http://127.0.0.1:8000`

## Notes

This version uses heuristics rather than full parser-driven compilation or transpilation. It is designed to give strong developer guidance and useful first-pass transformations while surfacing confidence and warnings where manual review is still important.
