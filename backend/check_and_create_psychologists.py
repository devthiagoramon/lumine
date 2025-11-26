"""
Script para verificar e criar psicólogos se necessário
"""
from app.database import SessionLocal
from app.models.usuario import User
from app.models.psicologo import Psychologist
from app.models.especialidade import Specialty
from app.models.abordagem import Approach
from app.auth import get_password_hash
import random

def check_and_create_psychologists():
    db = SessionLocal()
    
    try:
        # Verificar quantos psicólogos existem
        try:
            psychologists_count = db.query(Psychologist).count()
        except Exception as e:
            print(f"ERRO ao contar psicologos: {e}")
            print("Tentando recriar as tabelas...")
            from app.database import engine, Base
            Base.metadata.drop_all(bind=engine, tables=[Psychologist.__table__])
            Base.metadata.create_all(bind=engine, tables=[Psychologist.__table__])
            psychologists_count = db.query(Psychologist).count()
        
        print(f"Psicologos encontrados no banco: {psychologists_count}")
        
        if psychologists_count >= 5:
            print("Ja existem psicologos suficientes no banco!")
            # Listar os psicólogos
            psychologists = db.query(Psychologist).all()
            print("\nLista de psicologos:")
            for p in psychologists:
                user = db.query(User).filter(User.id == p.user_id).first()
                verified = "Verificado" if p.is_verified else "Nao verificado"
                print(f"  - {user.full_name if user else 'N/A'} ({p.crp}) - {verified}")
            return
        
        # Verificar se existem especialidades e abordagens
        specialties = db.query(Specialty).all()
        approaches = db.query(Approach).all()
        
        if not specialties or not approaches:
            print("ERRO: Execute primeiro o migrations_seed_data.py para criar especialidades e abordagens!")
            return
        
        print(f"\nEspecialidades disponiveis: {len(specialties)}")
        print(f"Abordagens disponiveis: {len(approaches)}")
        
        # Quantos precisamos criar
        needed = 5 - psychologists_count
        print(f"\nCriando {needed} psicologo(s)...")
        
        # Dados de psicólogos de exemplo
        psychologists_data = [
            {
                "email": "ana.silva@lumine.com",
                "full_name": "Ana Silva",
                "phone": "(11) 98765-4321",
                "crp": "06/123456",
                "bio": "Psicóloga clínica com 10 anos de experiência em TCC. Especializada no tratamento de ansiedade e depressão. Atendo online e presencialmente em São Paulo.",
                "experience_years": 10,
                "consultation_price": 200.0,
                "online_consultation": True,
                "in_person_consultation": True,
                "address": "Av. Paulista, 1000",
                "city": "São Paulo",
                "state": "SP",
                "zip_code": "01310-100",
                "specialty_names": ["Ansiedade", "Depressão"],
                "approach_names": ["TCC"]
            },
            {
                "email": "carlos.santos@lumine.com",
                "full_name": "Carlos Santos",
                "phone": "(21) 98765-4322",
                "crp": "05/234567",
                "bio": "Psicólogo especializado em terapia humanista e gestalt. Trabalho com desenvolvimento pessoal e autoestima. Atendimento online disponível.",
                "experience_years": 8,
                "consultation_price": 180.0,
                "online_consultation": True,
                "in_person_consultation": False,
                "address": "Rua das Flores, 200",
                "city": "Rio de Janeiro",
                "state": "RJ",
                "zip_code": "20000-000",
                "specialty_names": ["Autoestima", "Relacionamentos"],
                "approach_names": ["Humanista", "Gestalt"]
            },
            {
                "email": "maria.oliveira@lumine.com",
                "full_name": "Maria Oliveira",
                "phone": "(31) 98765-4323",
                "crp": "04/345678",
                "bio": "Psicóloga infantil e adolescente com formação em TCC e abordagem comportamental. Experiência em TDAH e desenvolvimento infantil.",
                "experience_years": 12,
                "consultation_price": 220.0,
                "online_consultation": True,
                "in_person_consultation": True,
                "address": "Av. Afonso Pena, 3000",
                "city": "Belo Horizonte",
                "state": "MG",
                "zip_code": "30130-000",
                "specialty_names": ["Infantil", "TDAH"],
                "approach_names": ["TCC", "Comportamental"]
            },
            {
                "email": "joao.ferreira@lumine.com",
                "full_name": "João Ferreira",
                "phone": "(41) 98765-4324",
                "crp": "08/456789",
                "bio": "Psicólogo clínico especializado em trauma e TEPT. Utilizo abordagem integrativa combinando técnicas de diferentes escolas terapêuticas.",
                "experience_years": 15,
                "consultation_price": 250.0,
                "online_consultation": True,
                "in_person_consultation": True,
                "address": "Rua XV de Novembro, 500",
                "city": "Curitiba",
                "state": "PR",
                "zip_code": "80020-000",
                "specialty_names": ["Trauma", "Estresse"],
                "approach_names": ["Integrativa", "TCC"]
            },
            {
                "email": "juliana.costa@lumine.com",
                "full_name": "Juliana Costa",
                "phone": "(51) 98765-4325",
                "crp": "07/567890",
                "bio": "Psicóloga com formação em psicanálise e terapia sistêmica. Especializada em terapia de casal e relacionamentos interpessoais.",
                "experience_years": 9,
                "consultation_price": 190.0,
                "online_consultation": True,
                "in_person_consultation": True,
                "address": "Av. Borges de Medeiros, 1500",
                "city": "Porto Alegre",
                "state": "RS",
                "zip_code": "90020-000",
                "specialty_names": ["Relacionamentos", "Autoestima"],
                "approach_names": ["Psicanálise", "Sistêmica"]
            }
        ]
        
        created_count = 0
        
        for i, psyc_data in enumerate(psychologists_data[:needed]):
            # Verificar se usuário já existe
            existing_user = db.query(User).filter(User.email == psyc_data["email"]).first()
            if existing_user:
                print(f"AVISO: Usuario {psyc_data['email']} ja existe. Pulando...")
                continue
            
            # Buscar especialidades e abordagens
            user_specialties = [s for s in specialties if s.name in psyc_data["specialty_names"]]
            user_approaches = [a for a in approaches if a.name in psyc_data["approach_names"]]
            
            if not user_specialties or not user_approaches:
                print(f"AVISO: Nao foi possivel encontrar todas as especialidades/abordagens para {psyc_data['full_name']}. Pulando...")
                continue
            
            # Criar usuário
            user = User(
                email=psyc_data["email"],
                hashed_password=get_password_hash("senha123"),
                full_name=psyc_data["full_name"],
                phone=psyc_data["phone"],
                is_psychologist=True,
                is_admin=False,
                is_active=True
            )
            db.add(user)
            db.flush()
            
            # Criar perfil de psicólogo
            psychologist = Psychologist(
                user_id=user.id,
                crp=psyc_data["crp"],
                bio=psyc_data["bio"],
                city=psyc_data["city"],
                state=psyc_data["state"],
                address=psyc_data.get("address"),
                zip_code=psyc_data.get("zip_code"),
                experience_years=psyc_data["experience_years"],
                consultation_price=psyc_data["consultation_price"],
                online_consultation=psyc_data["online_consultation"],
                in_person_consultation=psyc_data["in_person_consultation"],
                is_verified=True,  # Criar como verificado para aparecer na busca
                rating=round(random.uniform(4.0, 5.0), 1),
                total_reviews=random.randint(5, 50)
            )
            
            # Adicionar especialidades e abordagens
            psychologist.specialties = user_specialties
            psychologist.approaches = user_approaches
            
            db.add(psychologist)
            created_count += 1
            
            print(f"OK: Criado {psyc_data['full_name']} ({psyc_data['crp']}) - {psyc_data['city']}, {psyc_data['state']}")
        
        db.commit()
        print(f"\nSUCESSO: {created_count} psicologo(s) criado(s)!")
        print(f"Total de psicologos no banco: {db.query(Psychologist).count()}")
        
        # Listar todos os psicólogos
        print("\nLista completa de psicologos:")
        all_psychologists = db.query(Psychologist).all()
        for p in all_psychologists:
            user = db.query(User).filter(User.id == p.user_id).first()
            verified = "Verificado" if p.is_verified else "Nao verificado"
            print(f"  - {user.full_name if user else 'N/A'} ({p.crp}) - {verified}")
        
    except Exception as e:
        db.rollback()
        print(f"ERRO ao criar psicologos: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_and_create_psychologists()

