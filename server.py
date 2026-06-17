from __future__ import annotations

import sys


def run() -> None:
    try:
        import uvicorn
    except ImportError as error:
        raise SystemExit(
            "FastAPI runtime is not installed. Run `py -3 -m pip install -r requirements.txt`."
        ) from error

    uvicorn.run("app_backend.main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    sys.exit(run())
