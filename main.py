import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import openai

openai.api_key = os.getenv("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")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class NextQuestionRequest(BaseModel):
    currentIndex: int

class UserAnswer(BaseModel):
    question: str
    selected: int
    correct: int
    difficulty: int
    isCorrect: bool

class CurriculumRequest(BaseModel):
    userAnswers: Optional[List[UserAnswer]] = []

# Questions database
questions = [
    {
        "id": 1,
        "text": "What is the derivative of x²?",
        "choices": ["2x", "x", "x²", "1"],
        "correctIndex": 0,
        "difficulty": 1,
    },
    {
        "id": 2,
        "text": "Integral of 1/x dx is:",
        "choices": ["ln|x| + C", "x", "1/x² + C", "x² / 2"],
        "correctIndex": 0,
        "difficulty": 2,
    },
    {
        "id": 3,
        "text": "Limit of (sin x) / x as x approaches 0 is:",
        "choices": ["1", "0", "∞", "-1"],
        "correctIndex": 0,
        "difficulty": 2,
    },
    {
        "id": 4,
        "text": "Which method is best for solving the integral ∫ x e^x dx?",
        "choices": ["Integration by parts", "Substitution", "Partial fractions", "Trigonometric substitution"],
        "correctIndex": 0,
        "difficulty": 3,
    },
]

@app.post("/api/next-question")
async def next_question(req: NextQuestionRequest):
    idx = req.currentIndex
    if idx >= len(questions):
        return {"done": True}
    q = questions[idx]
    return {
        "done": False,
        "question": {
            "id": q["id"],
            "text": q["text"],
            "choices": q["choices"],
            "difficulty": q["difficulty"],
        }
    }

@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[msg.dict() for msg in req.messages],
            max_tokens=150,
            temperature=0.7,
        )
        chat_response = response.choices[0].message
        return {"reply": {"role": chat_response.role, "content": chat_response.content}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

@app.post("/api/generate-curriculum")
async def generate_curriculum(req: CurriculumRequest):
    user_answers = req.userAnswers or []
    curriculum = []
    for day in range(1, 31):
        topic = f"Day {day}: Foundations"
        explanation = f"Short explanation of concept for day {day}."
        practice = "https://www.khanacademy.org/math/calculus-1"
        video = "https://www.youtube.com/watch?v=WUvTyaaNkzM"

        # If the last answer was incorrect, focus on basics
        if user_answers and user_answers[-1].isCorrect is False:
            topic = f"Day {day}: Review Basics"
            explanation = "Additional practice for foundational concepts to strengthen your skills."

        curriculum.append({
            "day": day,
            "topic": topic,
            "explanation": explanation,
            "practice": practice,
            "video": video,
        })
    return {"curriculum": curriculum}
