#!/usr/bin/env python3
"""
Development server runner
"""
import uvicorn
from backend.main import app  # <== mana bu joy o‘zgardi

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",  # <== bu ham shunga mos bo‘lishi kerak
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
