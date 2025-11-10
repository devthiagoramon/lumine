from sqlalchemy import Column, Integer, String, Boolean, Text, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Tabela de associação para favoritos (deve ser definida antes de User)
favorites = Table(
    'favorites',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('psychologist_id', Integer, ForeignKey('psychologists.id'), primary_key=True)
)

# Tabela de associação para especialidades
psychologist_specialties = Table(
    'psychologist_specialties',
    Base.metadata,
    Column('psychologist_id', Integer, ForeignKey('psychologists.id')),
    Column('specialty_id', Integer, ForeignKey('specialties.id'))
)

# Tabela de associação para abordagens
psychologist_approaches = Table(
    'psychologist_approaches',
    Base.metadata,
    Column('psychologist_id', Integer, ForeignKey('psychologists.id')),
    Column('approach_id', Integer, ForeignKey('approaches.id'))
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    is_psychologist = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    psychologist_profile = relationship("Psychologist", back_populates="user", uselist=False)
    favorite_psychologists = relationship("Psychologist", secondary=favorites, backref="favorited_by")
    appointments = relationship("Appointment", foreign_keys="Appointment.user_id")
    reviews = relationship("Review", foreign_keys="Review.user_id")
    forum_posts = relationship("ForumPost", foreign_keys="ForumPost.user_id")
    forum_comments = relationship("ForumComment", foreign_keys="ForumComment.user_id")
    emotion_diaries = relationship("EmotionDiary", foreign_keys="EmotionDiary.user_id")
    payments = relationship("Payment", foreign_keys="Payment.user_id")

class Psychologist(Base):
    __tablename__ = "psychologists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    crp = Column(String, unique=True, nullable=False)  # Conselho Regional de Psicologia
    bio = Column(Text)
    experience_years = Column(Integer, default=0)
    consultation_price = Column(Float)
    online_consultation = Column(Boolean, default=True)
    in_person_consultation = Column(Boolean, default=False)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    profile_picture = Column(String)
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="psychologist_profile")
    specialties = relationship("Specialty", secondary=psychologist_specialties, back_populates="psychologists")
    approaches = relationship("Approach", secondary=psychologist_approaches, back_populates="psychologists")
    reviews = relationship("Review", back_populates="psychologist")
    appointments = relationship("Appointment", foreign_keys="Appointment.psychologist_id")

class Specialty(Base):
    __tablename__ = "specialties"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    
    psychologists = relationship("Psychologist", secondary=psychologist_specialties, back_populates="specialties")

class Approach(Base):
    __tablename__ = "approaches"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    
    psychologists = relationship("Psychologist", secondary=psychologist_approaches, back_populates="approaches")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    psychologist_id = Column(Integer, ForeignKey("psychologists.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    psychologist = relationship("Psychologist", back_populates="reviews")
    user = relationship("User", foreign_keys=[user_id])

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    psychologist_id = Column(Integer, ForeignKey("psychologists.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    appointment_type = Column(String, nullable=False)  # 'online' ou 'presencial'
    status = Column(String, default='pending')  # 'pending', 'confirmed', 'cancelled', 'completed'
    notes = Column(Text)
    payment_status = Column(String, default='pending')  # 'pending', 'paid', 'failed', 'refunded'
    payment_id = Column(String)  # ID do pagamento mockado
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    psychologist = relationship("Psychologist", foreign_keys=[psychologist_id])
    user = relationship("User", foreign_keys=[user_id])

class ForumPost(Base):
    __tablename__ = "forum_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, default='geral')  # 'geral', 'ansiedade', 'depressao', 'relacionamentos', etc.
    is_anonymous = Column(Boolean, default=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[user_id])
    comments = relationship("ForumComment", back_populates="post", cascade="all, delete-orphan")

class ForumComment(Base):
    __tablename__ = "forum_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("forum_posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_anonymous = Column(Boolean, default=False)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    post = relationship("ForumPost", back_populates="comments")
    user = relationship("User", foreign_keys=[user_id])

class EmotionDiary(Base):
    __tablename__ = "emotion_diaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    emotion = Column(String, nullable=False)  # 'feliz', 'triste', 'ansioso', 'irritado', 'calmo', etc.
    intensity = Column(Integer, nullable=False)  # 1-10
    notes = Column(Text)
    tags = Column(String)  # Tags separadas por vírgula
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", foreign_keys=[user_id])

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)  # 'credit_card', 'debit_card', 'pix', 'boleto'
    status = Column(String, default='pending')  # 'pending', 'paid', 'failed', 'refunded'
    payment_id = Column(String, unique=True)  # ID do pagamento mockado
    transaction_id = Column(String)  # ID da transação mockada
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    appointment = relationship("Appointment", foreign_keys=[appointment_id])
    user = relationship("User", foreign_keys=[user_id])

