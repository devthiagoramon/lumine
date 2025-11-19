from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Schemas de Autenticação
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    is_psychologist: bool = False

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    is_active: bool
    is_psychologist: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schemas de Especialidade e Abordagem
class SpecialtyBase(BaseModel):
    name: str
    description: Optional[str] = None

class SpecialtyResponse(SpecialtyBase):
    id: int
    
    class Config:
        from_attributes = True

class ApproachBase(BaseModel):
    name: str
    description: Optional[str] = None

class ApproachResponse(ApproachBase):
    id: int
    
    class Config:
        from_attributes = True

# Schemas de Psicólogo
class PsychologistBase(BaseModel):
    crp: str
    bio: Optional[str] = None
    experience_years: int = 0
    consultation_price: Optional[float] = None
    online_consultation: bool = True
    in_person_consultation: bool = False
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    profile_picture: Optional[str] = None

class PsychologistCreate(PsychologistBase):
    specialty_ids: List[int] = []
    approach_ids: List[int] = []

class PsychologistUpdate(BaseModel):
    bio: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_price: Optional[float] = None
    online_consultation: Optional[bool] = None
    in_person_consultation: Optional[bool] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    profile_picture: Optional[str] = None
    specialty_ids: Optional[List[int]] = None
    approach_ids: Optional[List[int]] = None

class PsychologistResponse(PsychologistBase):
    id: int
    user_id: int
    rating: float
    total_reviews: int
    is_verified: bool
    created_at: datetime
    specialties: List[SpecialtyResponse] = []
    approaches: List[ApproachResponse] = []
    user: UserResponse
    
    class Config:
        from_attributes = True

class PsychologistListItem(BaseModel):
    id: int
    user_id: int
    crp: str
    bio: Optional[str]
    experience_years: int
    consultation_price: Optional[float]
    online_consultation: bool
    in_person_consultation: bool
    city: Optional[str]
    state: Optional[str]
    profile_picture: Optional[str]
    rating: float
    total_reviews: int
    is_verified: bool
    user: UserResponse
    specialties: List[SpecialtyResponse] = []
    approaches: List[ApproachResponse] = []
    
    class Config:
        from_attributes = True

# Schemas de Busca
class SearchFilters(BaseModel):
    query: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    specialty_ids: Optional[List[int]] = None
    approach_ids: Optional[List[int]] = None
    online_consultation: Optional[bool] = None
    in_person_consultation: Optional[bool] = None
    min_rating: Optional[float] = None
    max_price: Optional[float] = None
    min_experience: Optional[int] = None

class SearchResponse(BaseModel):
    psychologists: List[PsychologistListItem]
    total: int
    page: int
    page_size: int

# Schemas de Review
class ReviewCreate(BaseModel):
    psychologist_id: int
    rating: int
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    psychologist_id: int
    user_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    user: UserResponse
    
    class Config:
        from_attributes = True

# Schemas de Agendamento
class AppointmentCreate(BaseModel):
    psychologist_id: int
    appointment_date: datetime
    appointment_type: str  # 'online' ou 'presencial'
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    appointment_type: Optional[str] = None
    status: Optional[str] = None  # 'pending', 'confirmed', 'cancelled', 'completed'
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    psychologist_id: int
    user_id: int
    appointment_date: datetime
    appointment_type: str
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    psychologist: PsychologistListItem
    user: UserResponse
    
    class Config:
        from_attributes = True

# Schemas de Favoritos
class FavoriteResponse(BaseModel):
    psychologist: PsychologistListItem
    
    class Config:
        from_attributes = True

# Schemas de Fórum
class ForumPostCreate(BaseModel):
    title: str
    content: str
    category: str = 'geral'
    is_anonymous: bool = False

class ForumPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None

class ForumPostResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    category: str
    is_anonymous: bool
    views: int
    likes: int
    created_at: datetime
    updated_at: Optional[datetime]
    user: Optional[UserResponse] = None
    comments_count: int = 0
    
    class Config:
        from_attributes = True

class ForumCommentCreate(BaseModel):
    content: str
    is_anonymous: bool = False

class ForumCommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    is_anonymous: bool
    likes: int
    created_at: datetime
    updated_at: Optional[datetime]
    user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True

# Schemas de Diário de Emoção
class EmotionDiaryCreate(BaseModel):
    date: datetime
    emotion: str
    intensity: int  # 1-10
    notes: Optional[str] = None
    tags: Optional[str] = None

class EmotionDiaryUpdate(BaseModel):
    date: Optional[datetime] = None
    emotion: Optional[str] = None
    intensity: Optional[int] = None
    notes: Optional[str] = None
    tags: Optional[str] = None

class EmotionDiaryResponse(BaseModel):
    id: int
    user_id: int
    date: datetime
    emotion: str
    intensity: int
    notes: Optional[str]
    tags: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Schemas de Pagamento
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

# Schemas de Disponibilidade
class PsychologistAvailabilityCreate(BaseModel):
    day_of_week: int  # 0=Segunda, 1=Terça, ..., 6=Domingo
    start_time: str  # Formato HH:MM
    end_time: str  # Formato HH:MM
    is_available: bool = True

class PsychologistAvailabilityUpdate(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_available: Optional[bool] = None

class PsychologistAvailabilityResponse(BaseModel):
    id: int
    psychologist_id: int
    day_of_week: int
    start_time: str
    end_time: str
    is_available: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Schemas de Notificação
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    related_id: Optional[int]
    related_type: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

# Schemas de Questionário
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

# Schemas de Pré-cadastro de Psicólogo
class PsychologistPreRegistrationCreate(BaseModel):
    crp: str
    bio: Optional[str] = None
    experience_years: int = 0
    consultation_price: Optional[float] = None
    online_consultation: bool = True
    in_person_consultation: bool = False
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    specialty_ids: List[int] = []
    approach_ids: List[int] = []

class PsychologistPreRegistrationResponse(BaseModel):
    id: int
    user_id: int
    crp: str
    bio: Optional[str]
    experience_years: int
    consultation_price: Optional[float]
    online_consultation: bool
    in_person_consultation: bool
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    status: str
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Schemas de Saque
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

# Schemas de Agendamento (atualizado)
class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    appointment_type: Optional[str] = None
    status: Optional[str] = None  # 'pending', 'confirmed', 'cancelled', 'completed', 'rejected'
    notes: Optional[str] = None
    rejection_reason: Optional[str] = None

