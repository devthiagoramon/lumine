"""
Payment Schemas
"""
from pydantic import BaseModel, Field
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
    appointment_id: int = Field(alias="id_agendamento", serialization_alias="appointment_id")
    user_id: int = Field(alias="id_usuario", serialization_alias="user_id")
    amount: float = Field(alias="valor", serialization_alias="amount")
    payment_method: str = Field(alias="metodo_pagamento", serialization_alias="payment_method")
    status: str
    payment_id: str = Field(alias="id_pagamento", serialization_alias="payment_id")
    transaction_id: Optional[str] = Field(default=None, alias="id_transacao", serialization_alias="transaction_id")
    created_at: datetime = Field(alias="criado_em", serialization_alias="created_at")
    updated_at: Optional[datetime] = Field(default=None, alias="atualizado_em", serialization_alias="updated_at")
    
    class Config:
        from_attributes = True
        populate_by_name = True

