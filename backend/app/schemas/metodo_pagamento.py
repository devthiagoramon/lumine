"""
Payment Method Schemas
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
import re

class PaymentMethodCreate(BaseModel):
    card_type: str  # 'credit_card', 'debit_card'
    card_number: str
    card_holder: str
    card_expiry: str  # MM/YY
    card_cvv: str
    is_default: bool = False
    
    @validator('card_number')
    def validate_card_number(cls, v):
        # Remover espaços e caracteres não numéricos
        cleaned = re.sub(r'\s+', '', v)
        if not cleaned.isdigit() or len(cleaned) < 13 or len(cleaned) > 19:
            raise ValueError('Número do cartão inválido')
        return cleaned
    
    @validator('card_expiry')
    def validate_card_expiry(cls, v):
        # Validar formato MM/YY
        if not re.match(r'^\d{2}/\d{2}$', v):
            raise ValueError('Data de validade deve estar no formato MM/AA')
        month, year = v.split('/')
        if int(month) < 1 or int(month) > 12:
            raise ValueError('Mês inválido')
        return v
    
    @validator('card_cvv')
    def validate_card_cvv(cls, v):
        if not v.isdigit() or len(v) < 3 or len(v) > 4:
            raise ValueError('CVV inválido')
        return v

class PaymentMethodUpdate(BaseModel):
    card_holder: Optional[str] = None
    card_expiry: Optional[str] = None
    is_default: Optional[bool] = None
    
    @validator('card_expiry')
    def validate_card_expiry(cls, v):
        if v is not None:
            if not re.match(r'^\d{2}/\d{2}$', v):
                raise ValueError('Data de validade deve estar no formato MM/AA')
            month, year = v.split('/')
            if int(month) < 1 or int(month) > 12:
                raise ValueError('Mês inválido')
        return v

class PaymentMethodResponse(BaseModel):
    id: int
    user_id: int
    card_type: str
    card_brand: Optional[str]
    last_four_digits: str
    card_holder: str
    expiry_month: str
    expiry_year: str
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True



