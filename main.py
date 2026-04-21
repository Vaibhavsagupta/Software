import os
import sys

# Add backend to path so imports like 'database' or 'routes' work
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7070)
