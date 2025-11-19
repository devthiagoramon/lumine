"""
Withdrawal Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WithdrawalCreate(BaseModel):
    amount: float
    bank_name: str
    bank_account: str
    bank_agency: str
    account_type: str  # 'checking' ou 'savings'

class WithdrawalResponse(BaseModel):
    id: int
    psychologist_id: int
    amount: float
    bank_name: str
    bank_account: str
    bank_agency: str
    account_type: str
    status: str
    rejection_reason: Optional[str]
    processed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

