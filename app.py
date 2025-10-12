from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    message: str

@app.get("/")
async def home():
    return {"message": "🤖 Fast Chatbot backend running!"}

@app.post("/chat")
async def chat(query: Query):
    try:
        print(f"📨 Received query: {query.message}")
        
        from rag_engine import get_answer
        response = get_answer(query.message)
        
        return {"reply": response}
        
    except Exception as e:
        print(f"🚨 Error in /chat endpoint: {e}")
        return {"reply": "I'm having trouble right now. Please try again in a moment."}

@app.on_event("startup")
async def startup_event():
    try:
        from rag_engine import create_knowledge_base
        create_knowledge_base()
        print("✅ Startup completed successfully!")
    except Exception as e:
        print(f"❌ Startup error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)