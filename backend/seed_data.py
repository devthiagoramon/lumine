"""
Script para popular o banco de dados com dados iniciais
"""
from app.database import SessionLocal, engine
from app.models import Base, Specialty, Approach, User, Psychologist
from app.auth import get_password_hash

# Criar tabelas
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Especialidades
    specialties_data = [
        {"name": "Ansiedade", "description": "Tratamento de transtornos de ansiedade"},
        {"name": "Depressão", "description": "Tratamento de depressão e transtornos do humor"},
        {"name": "TDAH", "description": "Transtorno de Déficit de Atenção e Hiperatividade"},
        {"name": "TOC", "description": "Transtorno Obsessivo Compulsivo"},
        {"name": "Trauma", "description": "Tratamento de traumas e TEPT"},
        {"name": "Relacionamentos", "description": "Terapia de casal e relacionamentos"},
        {"name": "Autoestima", "description": "Desenvolvimento pessoal e autoestima"},
        {"name": "Luto", "description": "Processamento de luto e perdas"},
        {"name": "Estresse", "description": "Gerenciamento de estresse"},
        {"name": "Infantil", "description": "Psicologia infantil"},
    ]
    
    for spec_data in specialties_data:
        existing = db.query(Specialty).filter(Specialty.name == spec_data["name"]).first()
        if not existing:
            specialty = Specialty(**spec_data)
            db.add(specialty)
    
    # Abordagens
    approaches_data = [
        {"name": "TCC", "description": "Terapia Cognitivo-Comportamental"},
        {"name": "Psicanálise", "description": "Abordagem psicanalítica"},
        {"name": "Humanista", "description": "Abordagem humanista"},
        {"name": "Gestalt", "description": "Terapia Gestalt"},
        {"name": "Comportamental", "description": "Análise do Comportamento"},
        {"name": "Sistêmica", "description": "Terapia Sistêmica"},
        {"name": "Fenomenológica", "description": "Abordagem fenomenológica"},
        {"name": "Integrativa", "description": "Abordagem integrativa"},
    ]
    
    for app_data in approaches_data:
        existing = db.query(Approach).filter(Approach.name == app_data["name"]).first()
        if not existing:
            approach = Approach(**app_data)
            db.add(approach)
    
    # Criar usuário administrador padrão
    admin_email = "admin@lumine.com"
    admin_password = "admin123"  # Altere esta senha em produção!
    
    existing_admin = db.query(User).filter(User.email == admin_email).first()
    if not existing_admin:
        try:
            # Usar a função corrigida que trata o limite de 72 bytes
            hashed_password = get_password_hash(admin_password)
            admin_user = User(
                email=admin_email,
                hashed_password=hashed_password,
                full_name="Administrador",
                is_admin=True,
                is_psychologist=False,
                is_active=True
            )
            db.add(admin_user)
            print(f"SUCESSO: Usuario administrador criado!")
            print(f"   Email: {admin_email}")
            print(f"   Senha: {admin_password}")
            print(f"   IMPORTANTE: Altere a senha apos o primeiro login!")
        except Exception as e:
            print(f"AVISO: Erro ao criar admin com passlib: {e}")
            print("   Tentando com bcrypt diretamente...")
            # Fallback: usar bcrypt diretamente
            import bcrypt
            salt = bcrypt.gensalt()
            password_bytes = admin_password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
            admin_user = User(
                email=admin_email,
                hashed_password=hashed_password,
                full_name="Administrador",
                is_admin=True,
                is_psychologist=False,
                is_active=True
            )
            db.add(admin_user)
            print(f"SUCESSO: Usuario administrador criado com bcrypt direto!")
            print(f"   Email: {admin_email}")
            print(f"   Senha: {admin_password}")
    else:
        print("INFO: Usuario administrador ja existe")
    
    db.commit()
    print("\nSUCESSO: Dados iniciais criados com sucesso!")
    
except Exception as e:
    print(f"ERRO ao criar dados iniciais: {e}")
    db.rollback()
finally:
    db.close()

