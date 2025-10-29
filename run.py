"""Main runner for Merchant Image Validator Agent"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host="127.0.0.1",  # Use localhost instead of 0.0.0.0 for browser access
        port=8000,
        reload=True,
        log_level="info"
    )
