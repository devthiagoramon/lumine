"""
Payment Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentCreate(BaseModel):
    appointment_id: int
    payment_method: str  # 'credit_card', 'debit_card', 'pix', 'boleto'
    card_number: Optional[str] = None
    card_holder: Optional[str] = None
    card_expiry: Optional[str] = None
    card_cvv: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    appointment_id: int
    user_id: int
    amount: float
    payment_method: str
    status: str
    payment_id: str
    transaction_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

