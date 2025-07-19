from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from backend.llm.robot_girl_agent import RobotGirlAgent
from backend.llm.message_reply_advisor import MessageReplyAdvisor
from backend.llm.agents import DatingAnalyzer, GeneralDatingAdvisor

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

girl = RobotGirlAgent()
advisor = MessageReplyAdvisor()
profile_analyzer = DatingAnalyzer()
dating_coach = GeneralDatingAdvisor()

class Message(BaseModel):
    user_message: str

class ProfileBio(BaseModel):
    bio: str

class CoachQuestion(BaseModel):
    question: str

@app.post("/chat")
def chat(msg: Message):
    reply = girl.respond_to_message(msg.user_message)
    suggestion = advisor.suggest_reply(girl.conversation_history, reply)
    return {"reply": reply, "advice": suggestion}

@app.post("/analyze-profile")
def analyze_profile(bio: ProfileBio):
    feedback = profile_analyzer.profile_bio_advisor(bio.bio)
    return {"feedback": feedback}

@app.post("/ask-coach")
def ask_coach(q: CoachQuestion):
    answer = dating_coach.ask_question(q.question)
    return {"answer": answer}

@app.get("/", response_class=HTMLResponse)
def index():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
