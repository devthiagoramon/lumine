"""
Questionnaire Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QuestionnaireCreate(BaseModel):
    question_1: int  # 1-5
    question_2: int
    question_3: int
    question_4: int
    question_5: int
    question_6: int
    question_7: int
    question_8: int
    question_9: int
    question_10: int

class QuestionnaireResponse(BaseModel):
    id: int
    user_id: int
    question_1: Optional[int]
    question_2: Optional[int]
    question_3: Optional[int]
    question_4: Optional[int]
    question_5: Optional[int]
    question_6: Optional[int]
    question_7: Optional[int]
    question_8: Optional[int]
    question_9: Optional[int]
    question_10: Optional[int]
    total_score: Optional[int]
    recommendation: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

