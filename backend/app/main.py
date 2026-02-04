"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api.routes import router
from .database.history import history_manager
from .database.connection import history_db, target_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting Text-to-SQL Agent API...")
    
    # Initialize database
    await history_manager.init_database()
    print("✓ Database initialized")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await history_db.close()
    await target_db.close()


# Create FastAPI app
app = FastAPI(
    title="Text-to-SQL Agent API",
    description="AI-powered chatbot that converts natural language to SQL",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Text-to-SQL Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
