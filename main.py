from fastapi import FastAPI
from routes.auth_routes import router as auth_router

app = FastAPI(title="RegenAI API", version="1.0.0")

# Include auth routes
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

@app.get("/")
def read_root():
    return {"message": "Welcome to RegenAI API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
