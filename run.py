from pathlib import Path
import uvicorn

if __name__ == "__main__":
    print("Persian ML web app: http://127.0.0.1:8000")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
