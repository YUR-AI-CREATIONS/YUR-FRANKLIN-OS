"""
Main application entry point
TODO: Add authentication middleware
TODO: Implement rate limiting
"""
from fastapi import FastAPI
from routes import user_router

app = FastAPI(title="My API")
app.include_router(user_router)

# TODO: Add database connection
# BUG: Memory leak in production

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
