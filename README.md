# Code Humanizer

A lightweight app with a Python backend that rewrites NLP chatbot code into more human-like, readable code across multiple languages.

## What it does

- Serves the UI and API from a tiny Python HTTP server
- Auto-detects likely language or accepts a language hint
- Recognizes common NLP chatbot patterns such as prompts, conversation state, LLM calls, and routing
- Adds an optional summary comment at the top of the snippet
- Expands common shorthand identifiers such as `usr` to `user`
- Normalizes indentation and spacing
- Generates a plain-English walkthrough of the snippet

## Run it

Run:

```bash
python server.py
```

Then open `http://127.0.0.1:8000`.

## Notes

The backend logic lives in `humanizer.py` and uses heuristic transformations rather than full language parsers, so it works best as a readability improver for chatbot-oriented code rather than a perfect source-to-source compiler.
