"""
Script para criar psicólogos de exemplo para teste
"""
from app.database import SessionLocal
from app.models import User, Psychologist, Specialty, Approach
from app.auth import get_password_hash
import random

def create_sample_psychologists():
    db = SessionLocal()
    
    try:
        # Pegar especialidades e abordagens existentes
        specialties = db.query(Specialty).all()
        approaches = db.query(Approach).all()
        
        if not specialties or not approaches:
            print("ERRO: Execute primeiro o seed_data.py para criar especialidades e abordagens!")
            return
        
        # Dados de psicólogos de exemplo
        sample_psychologists = [
            {
                "email": "maria.silva@example.com",
                "password": "senha123",
                "full_name": "Maria Silva",
                "crp": "06/123456",
                "bio": "Psicóloga clínica com experiência em terapia cognitivo-comportamental. Especializada em ansiedade e depressão.",
                "city": "São Paulo",
                "state": "SP",
                "experience_years": 5,
                "consultation_price": 150.00,
                "online_consultation": True,
                "in_person_consultation": True,
                "specialties": ["Ansiedade", "Depressão"],
                "approaches": ["TCC"]
            },
            {
                "email": "joao.santos@example.com",
                "password": "senha123",
                "full_name": "João Santos",
                "crp": "06/234567",
                "bio": "Psicólogo especializado em relacionamentos e terapia de casais. Abordagem humanista e sistêmica.",
                "city": "Rio de Janeiro",
                "state": "RJ",
                "experience_years": 8,
                "consultation_price": 180.00,
                "online_consultation": True,
                "in_person_consultation": False,
                "specialties": ["Relacionamentos"],
                "approaches": ["Humanista", "Sistêmica"]
            },
            {
                "email": "ana.oliveira@example.com",
                "password": "senha123",
                "full_name": "Ana Oliveira",
                "crp": "06/345678",
                "bio": "Psicóloga infantil com formação em TDAH e desenvolvimento infantil. Experiência com crianças e adolescentes.",
                "city": "Belo Horizonte",
                "state": "MG",
                "experience_years": 3,
                "consultation_price": 130.00,
                "online_consultation": True,
                "in_person_consultation": True,
                "specialties": ["Infantil", "TDAH"],
                "approaches": ["TCC", "Comportamental"]
            },
            {
                "email": "carlos.pereira@example.com",
                "password": "senha123",
                "full_name": "Carlos Pereira",
                "crp": "06/456789",
                "bio": "Psicólogo especializado em trauma e TEPT. Utilizo técnicas de EMDR e terapia cognitiva.",
                "city": "Curitiba",
                "state": "PR",
                "experience_years": 10,
                "consultation_price": 200.00,
                "online_consultation": False,
                "in_person_consultation": True,
                "specialties": ["Trauma"],
                "approaches": ["TCC"]
            },
            {
                "email": "julia.costa@example.com",
                "password": "senha123",
                "full_name": "Julia Costa",
                "crp": "06/567890",
                "bio": "Psicóloga com foco em autoestima e desenvolvimento pessoal. Abordagem gestalt e humanista.",
                "city": "Porto Alegre",
                "state": "RS",
                "experience_years": 6,
                "consultation_price": 160.00,
                "online_consultation": True,
                "in_person_consultation": True,
                "specialties": ["Autoestima"],
                "approaches": ["Gestalt", "Humanista"]
            }
        ]
        
        created_count = 0
        
        for psyc_data in sample_psychologists:
            # Verificar se usuário já existe
            existing_user = db.query(User).filter(User.email == psyc_data["email"]).first()
            if existing_user:
                print(f"Usuario {psyc_data['email']} ja existe. Pulando...")
                continue
            
            # Criar usuário
            user = User(
                email=psyc_data["email"],
                hashed_password=get_password_hash(psyc_data["password"]),
                full_name=psyc_data["full_name"],
                is_psychologist=True,
                is_admin=False,
                is_active=True
            )
            db.add(user)
            db.flush()  # Para obter o ID do usuário
            
            # Buscar especialidades e abordagens
            user_specialties = [s for s in specialties if s.name in psyc_data["specialties"]]
            user_approaches = [a for a in approaches if a.name in psyc_data["approaches"]]
            
            # Criar perfil de psicólogo
            psychologist = Psychologist(
                user_id=user.id,
                crp=psyc_data["crp"],
                bio=psyc_data["bio"],
                city=psyc_data["city"],
                state=psyc_data["state"],
                experience_years=psyc_data["experience_years"],
                consultation_price=psyc_data["consultation_price"],
                online_consultation=psyc_data["online_consultation"],
                in_person_consultation=psyc_data["in_person_consultation"],
                is_verified=True,  # Já criar como verificado para aparecer na busca
                specialties=user_specialties,
                approaches=user_approaches
            )
            db.add(psychologist)
            created_count += 1
            
            print(f"Criado: {psyc_data['full_name']} ({psyc_data['crp']})")
        
        db.commit()
        print(f"\nSUCESSO: {created_count} psicologo(s) de exemplo criado(s)!")
        print("\nCredenciais de login:")
        print("Email: qualquer email acima")
        print("Senha: senha123")
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_psychologists()

