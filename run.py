"""Main runner for Merchant Image Validator Agent"""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Railway sets PORT automatically
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",  # Required for Railway
        port=port,
        reload=True,
        log_level="info"
    )
