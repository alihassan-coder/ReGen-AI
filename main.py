from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth_routes import router as auth_router
from routes.forme_routes import router as forms_router
from routes.agent_routes import router as agent_router

app = FastAPI(title="RegenAI API", version="1.0.0")

# CORS middleware to allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(forms_router)
app.include_router(agent_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to RegenAI API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
