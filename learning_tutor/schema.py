from pydantic import BaseModel
from typing import List, Optional


class TutorResponse(BaseModel):
    explanation: str
    example: str
    practice_task: str
    follow_up_question: str
    difficulty_level: Optional[str] = None


class QuizResponse(BaseModel):
    question: str
    options: List[str]
    answer: str