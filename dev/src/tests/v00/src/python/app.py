"""
Python application module for test repository v00.
"""

from fastapi import FastAPI

app = FastAPI(title="Test Repository v00 API")


@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Hello from Python FastAPI!"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


def main():
    """Main function."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

