"""
Payment Method Schemas
"""
from pydantic import BaseModel, Field, field_validator
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
    
    @field_validator('card_number', mode='before')
    @classmethod
    def validate_card_number(cls, v):
        if not isinstance(v, str):
            raise ValueError('Número do cartão deve ser uma string')
        # Remover espaços e caracteres não numéricos
        cleaned = re.sub(r'\s+', '', v)
        if not cleaned.isdigit() or len(cleaned) < 13 or len(cleaned) > 19:
            raise ValueError('Número do cartão inválido')
        return cleaned
    
    @field_validator('card_expiry', mode='before')
    @classmethod
    def validate_card_expiry(cls, v):
        if not isinstance(v, str):
            raise ValueError('Data de validade deve ser uma string')
        # Validar formato MM/YY
        if not re.match(r'^\d{2}/\d{2}$', v):
            raise ValueError('Data de validade deve estar no formato MM/AA')
        month, year = v.split('/')
        if int(month) < 1 or int(month) > 12:
            raise ValueError('Mês inválido')
        return v
    
    @field_validator('card_cvv', mode='before')
    @classmethod
    def validate_card_cvv(cls, v):
        if not isinstance(v, str):
            raise ValueError('CVV deve ser uma string')
        if not v.isdigit() or len(v) < 3 or len(v) > 4:
            raise ValueError('CVV inválido')
        return v

class PaymentMethodUpdate(BaseModel):
    card_holder: Optional[str] = None
    card_expiry: Optional[str] = None
    is_default: Optional[bool] = None
    
    @field_validator('card_expiry')
    @classmethod
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
    user_id: int = Field(alias="id_usuario")
    card_type: str = Field(alias="tipo_cartao")
    card_brand: Optional[str] = Field(alias="bandeira", default=None)
    last_four_digits: str = Field(alias="ultimos_quatro_digitos")
    card_holder: str = Field(alias="portador")
    expiry_month: str = Field(alias="mes_validade")
    expiry_year: str = Field(alias="ano_validade")
    is_default: bool = Field(alias="eh_padrao")
    created_at: datetime = Field(alias="criado_em")
    updated_at: Optional[datetime] = Field(alias="atualizado_em", default=None)
    
    class Config:
        from_attributes = True
        populate_by_name = True



