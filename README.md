# 🧠 Code Humanizer V2

> An AI-oriented code transformation platform that makes code more readable, converts it across languages, generates snippets from natural language, and builds developer career artifacts — all powered by heuristic analysis.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES_Modules-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## ✨ Features

### 🔧 Intelligent Code Humanization
- **Identifier Expansion** — Automatically renames cryptic variables (`acct` → `account`, `usr_msg` → `userMessage`) while preserving casing style (snake_case, camelCase, PascalCase, CONSTANT_CASE).
- **Docstring Generation** — Inserts docstrings into Python function definitions automatically.
- **Spacing Normalization** — Cleans up whitespace, tabs, indentation, and trailing spaces.
- **Refactor Modes** — Choose a target audience: `beginner`, `intermediate`, `professional`, or `production`.
- **Complexity Analysis** — Estimates cyclomatic complexity based on conditionals, loops, and function frequency.
- **Dead Code Detection** — Flags unreachable conditionals (`if false`), sequential returns, and unused variable declarations.
- **Chatbot / LLM Signal Detection** — Identifies patterns like RAG retrieval, prompt building, intent routing, and message history handling.
- **Step-by-Step Walkthrough** — Generates insight cards explaining what each transformation did and why.

### 🔄 Polyglot Code Conversion
- Bidirectional translation across **C**, **C++**, **Java**, and **Python**.
- Handles function signatures, variable type inference, loop translation, print statements, brace/indentation adaptation, and automatic `main()` wrapping.
- Returns a **confidence score** (0–100%) and **warnings** for unsupported features (templates, dynamic memory, multithreading, etc.).

### ✍️ Natural Language Code Generation
Generate code from plain-English prompts across **13 built-in algorithms**:

| Algorithm | Description |
|---|---|
| Hello World | Basic output program |
| Factorial | Recursive & iterative |
| Fibonacci | Recursive & iterative |
| Bubble Sort | Array sorting |
| Binary Search | Sorted array search |
| Prime Check | Simple check & Sieve of Eratosthenes |
| Linked List | Node creation, append, display, delete |
| Stack | Push, pop, peek, empty check |
| Reverse String | String reversal |
| Palindrome Check | String palindrome detection |
| Calculator | Basic arithmetic operations |
| File I/O | Read/write operations |
| Matrix Multiplication | 2D matrix product |

Supports output in **Python**, **C**, **C++**, and **Java** with match confidence and fallback suggestions.

### 📊 Code Quality Dashboard
Six real-time metrics scored 0–100:
- **Readability** — Based on average line length and comment density
- **Maintainability** — Based on cyclomatic complexity and dead code occurrences
- **Complexity Score** — Inverse mapping of calculated complexity
- **Security Score** — Based on count of flagged security findings
- **Humanization Score** — Average of readability, maintainability, and security
- **Overall Score** — Floor average of all five scores

### 🔒 Static Security Scanning (SAST)
Heuristic scan for **8 security risks** with severity ratings and remediation guidance:

| Risk | Severity |
|---|---|
| `eval()` usage | 🔴 High |
| `exec()` usage | 🔴 High |
| SQL Injection patterns | 🔴 High |
| Hardcoded credentials / API keys | 🔴 High |
| Unsafe deserialization (`pickle.loads`, `yaml.load`) | 🔴 High |
| Command injection (`os.system`, `subprocess`) | 🔴 High |
| Unsafe file open operations | 🟡 Medium |
| XSS risks (`innerHTML`, `dangerouslySetInnerHTML`) | 🟡 Medium |

### 💼 Developer Career & Interview Assistant
- **Project Summary** — Professional statement summarizing the technical workflow
- **Resume Bullet Points** — 3 achievement-focused bullet points ready for your CV
- **Technical Highlights** — Detected language, quality score, and security posture
- **Interview Q&A** — 3 tailored technical questions with recommended response strategies
- **Complexity Explanation** — Plain-English breakdown of code complexity

### 🖥️ Dual UI Options
- **FastAPI SPA** — Monaco Editor, glassmorphic UI, dark/light theme toggle, drag-and-drop file loading, code copying and downloading
- **Streamlit App** — Premium dark-themed dashboard with sidebar configuration, tabbed layout, and interactive metrics

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core runtime |
| **FastAPI** | Async REST API framework |
| **Uvicorn** | ASGI web server |
| **Pydantic v2** | Data validation & schemas |
| **Standard Library** | `re`, `dataclasses`, `math`, `logging`, `pathlib` |

### Frontend — FastAPI SPA
| Technology | Purpose |
|---|---|
| **HTML5 & CSS3** | Structure & styling (CSS Variables, Glassmorphism, Responsive Grid) |
| **Vanilla JavaScript** | ES Modules, Promises, `fetch` API |
| **Monaco Editor** | VS Code editor engine (loaded via CDN) |

### Frontend — Streamlit
| Technology | Purpose |
|---|---|
| **Streamlit** | Python web UI framework |
| **Custom CSS** | Injected via `st.markdown` for premium styling |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### 1. Clone the Repository

```bash
git clone https://github.com/raghunath485/code_humanizer.git
cd code_humanizer
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

**Option A — FastAPI Web App (recommended):**

```bash
py -3 server.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

**Option B — Streamlit App:**

```bash
streamlit run streamlit_app.py
```

The application will launch in your default web browser.

---

## 🌐 API Reference

The FastAPI backend exposes the following REST endpoints:

### `GET /api/health`
Returns server status, version, supported conversion languages, and available concepts.

### `POST /api/humanize`
Humanizes the submitted code with all configured options.

**Request Body:**
```json
{
  "code": "def calc_val(x, y): return x + y",
  "options": {
    "rename_identifiers": true,
    "add_docstrings": true,
    "normalize_spacing": true,
    "add_summary_comment": true,
    "explain_complexity": true,
    "detect_dead_code": true,
    "language_hint": "python",
    "target_profile": "developer_friendly",
    "refactor_mode": "professional",
    "concept_preferences": ["Functions", "OOP"]
  }
}
```

**Response:** Humanized code, insights, quality metrics, security findings, dead code findings, and chatbot signals.

### `POST /api/convert`
Converts code between supported languages.

**Request Body:**
```json
{
  "code": "print('Hello World')",
  "source_language": "python",
  "target_language": "java"
}
```

**Response:** Translated code, confidence score (0–100%), and conversion warnings.

### `POST /api/assistant`
Generates developer career artifacts from code analysis.

**Request Body:**
```json
{
  "code": "def process_data(items): ...",
  "language_hint": "python"
}
```

**Response:** Project summary, resume bullet points, interview Q&A, technical highlights, and complexity explanations.

### Interactive Docs
- **Swagger UI:** [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)
- **ReDoc:** [http://127.0.0.1:8000/api/redoc](http://127.0.0.1:8000/api/redoc)

---

## 🗂️ Supported Languages

| Capability | Languages |
|---|---|
| **Language Detection** | Python, Java, C++, C, JavaScript, TypeScript |
| **Code Humanization** | Python, Java, C++, C, JavaScript, TypeScript |
| **Code Conversion** | C ↔ C++ ↔ Java ↔ Python |
| **Code Generation** | Python, C, C++, Java |

---

## 📂 Project Structure

```
code-humanizer/
├── app_backend/                    # Core Backend Package
│   ├── __init__.py                 # Package initializer
│   ├── main.py                     # FastAPI app, API routes, middleware & static routing
│   ├── schemas.py                  # Pydantic models & HumanizeOptions dataclass
│   ├── humanizer_engine.py         # Identifier expansion, docstrings, dead code, insights
│   ├── converter_engine.py         # C / C++ / Java / Python translation pipeline
│   ├── concept_engine.py           # 22 concept directives & refactor mode guidance
│   ├── quality_engine.py           # 6-dimension quality scoring calculations
│   ├── security_engine.py          # SAST security rules & risk analyzer
│   ├── career_engine.py            # Project summary, resume bullets, interview prep
│   ├── codegen_engine.py           # Template-based code synthesis from prompts
│   └── language_tools.py           # Regex language detection & comment lookup
│
├── index.html                      # Main SPA HTML structure (FastAPI UI)
├── app.js                          # SPA application logic & Monaco editor manager
├── services.js                     # Frontend API HTTP client
├── components.js                   # UI rendering component templates
├── styles.css                      # CSS stylesheet (Glassmorphism, Dark/Light themes)
│
├── streamlit_app.py                # Streamlit Web App (alternative frontend)
├── server.py                       # Server launcher script
├── humanizer.py                    # Public top-level re-export module
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
└── README.md                       # You are here
```

---

## 🎯 22 Supported Concept Preferences

Customize how your code is refactored by selecting from these developer concepts:

<details>
<summary>View all 22 concepts</summary>

1. Functions
2. Classes
3. Loops
4. Conditionals
5. Arrays
6. Lists
7. Dictionaries / Maps
8. Recursion
9. Exceptions
10. File Handling
11. OOP
12. Inheritance
13. Polymorphism
14. Interfaces
15. Generics
16. Multithreading
17. Async Programming
18. Lambda Expressions
19. Functional Programming
20. Design Patterns
21. Database Operations
22. API Calls

</details>

---

## 📝 Example

**Input:**
```python
def hndl_usr_msg(msg, llm_svc, sess_ctx):
    resp = llm_svc.gen_resp(msg=msg)
    return resp
```

**Humanized Output:**
```python
def handle_user_message(message, llm_service, session_context):
    """Process the incoming user message and return a generated response."""
    response = llm_service.generate_response(message=message)
    return response
```

---

## ⚠️ Notes

- This version uses **heuristics** rather than full parser-driven compilation or transpilation.
- It is designed to provide strong developer guidance and useful first-pass transformations while surfacing confidence scores and warnings where manual review is still important.
- Payload size is limited to **1 MiB** per request (returns `413 Request Entity Too Large` for oversized requests).

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
