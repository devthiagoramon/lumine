"""
Script completo para popular o banco de dados com dados mockados para testes
Execute após rodar as migrations do Alembic
"""
from app.database import SessionLocal, engine, Base
from app.models import (
    Specialty, Approach, User, Psychologist, Review, 
    Appointment, ForumPost, ForumComment, EmotionDiary, 
    Payment, PsychologistAvailability
)
from app.models.tabelas_associacao import favorites
from sqlalchemy import func
from app.auth import get_password_hash
from datetime import datetime, timedelta
import random

# NOTA: Execute as migrations do Alembic antes de rodar este script:
# alembic upgrade head

db = SessionLocal()

try:
    print("[*] Iniciando seed de dados mockados...")
    
    # Limpar dados existentes (exceto admin)
    print("[*] Limpando dados existentes...")
    # Limpar favoritos primeiro (tabela de associação)
    db.execute(favorites.delete())
    db.query(PsychologistAvailability).delete()
    db.query(Payment).delete()
    db.query(EmotionDiary).delete()
    db.query(ForumComment).delete()
    db.query(ForumPost).delete()
    db.query(Appointment).delete()
    db.query(Review).delete()
    db.query(Psychologist).delete()
    db.query(User).filter(User.eh_admin == False).delete()
    db.query(Approach).delete()
    db.query(Specialty).delete()
    db.commit()
    
    # ========== ESPECIALIDADES ==========
    print("[*] Criando especialidades...")
    specialties_data = [
        {"nome": "Ansiedade", "descricao": "Tratamento de transtornos de ansiedade"},
        {"nome": "Depressão", "descricao": "Tratamento de depressão e transtornos do humor"},
        {"nome": "TDAH", "descricao": "Transtorno de Déficit de Atenção e Hiperatividade"},
        {"nome": "TOC", "descricao": "Transtorno Obsessivo Compulsivo"},
        {"nome": "Trauma", "descricao": "Tratamento de traumas e TEPT"},
        {"nome": "Relacionamentos", "descricao": "Terapia de casal e relacionamentos"},
        {"nome": "Autoestima", "descricao": "Desenvolvimento pessoal e autoestima"},
        {"nome": "Luto", "descricao": "Processamento de luto e perdas"},
        {"nome": "Estresse", "descricao": "Gerenciamento de estresse"},
        {"nome": "Infantil", "descricao": "Psicologia infantil"},
    ]
    
    specialties = []
    for spec_data in specialties_data:
        specialty = Specialty(**spec_data)
        db.add(specialty)
        specialties.append(specialty)
    db.commit()
    print(f"[OK] {len(specialties)} especialidades criadas")
    
    # ========== ABORDAGENS ==========
    print("[*] Criando abordagens...")
    approaches_data = [
        {"nome": "TCC", "descricao": "Terapia Cognitivo-Comportamental"},
        {"nome": "Psicanálise", "descricao": "Abordagem psicanalítica"},
        {"nome": "Humanista", "descricao": "Abordagem humanista"},
        {"nome": "Gestalt", "descricao": "Terapia Gestalt"},
        {"nome": "Comportamental", "descricao": "Análise do Comportamento"},
        {"nome": "Sistêmica", "descricao": "Terapia Sistêmica"},
        {"nome": "Fenomenológica", "descricao": "Abordagem fenomenológica"},
        {"nome": "Integrativa", "descricao": "Abordagem integrativa"},
    ]
    
    approaches = []
    for app_data in approaches_data:
        approach = Approach(**app_data)
        db.add(approach)
        approaches.append(approach)
    db.commit()
    print(f"[OK] {len(approaches)} abordagens criadas")
    
    # ========== USUÁRIOS E PSICÓLOGOS ==========
    print("[*] Criando usuários e psicólogos...")
    
    # Dados mockados de psicólogos
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
            "specialty_ids": [1, 2],  # Ansiedade, Depressão
            "approach_ids": [1],  # TCC
            "is_verified": True
        },
        {
            "email": "carlos.santos@lumine.com",
            "full_name": "Carlos Santos",
            "phone": "(21) 98765-4322",
            "crp": "05/234567",
            "bio": "Psicólogo especializado em terapia de casal e relacionamentos. Abordagem humanista e sistêmica. Atendo na Zona Sul do Rio de Janeiro.",
            "experience_years": 8,
            "consultation_price": 250.0,
            "online_consultation": True,
            "in_person_consultation": True,
            "address": "Rua das Laranjeiras, 500",
            "city": "Rio de Janeiro",
            "state": "RJ",
            "zip_code": "22240-000",
            "specialty_ids": [6],  # Relacionamentos
            "approach_ids": [3, 6],  # Humanista, Sistêmica
            "is_verified": True
        },
        {
            "email": "maria.oliveira@lumine.com",
            "full_name": "Maria Oliveira",
            "phone": "(31) 98765-4323",
            "crp": "04/345678",
            "bio": "Psicóloga infantil com formação em TCC e análise do comportamento. Atendo crianças e adolescentes. Consultas online disponíveis.",
            "experience_years": 12,
            "consultation_price": 180.0,
            "online_consultation": True,
            "in_person_consultation": False,
            "address": "Av. Afonso Pena, 2000",
            "city": "Belo Horizonte",
            "state": "MG",
            "zip_code": "30130-000",
            "specialty_ids": [10, 1],  # Infantil, Ansiedade
            "approach_ids": [1, 5],  # TCC, Comportamental
            "is_verified": True
        },
        {
            "email": "joao.ferreira@lumine.com",
            "full_name": "João Ferreira",
            "phone": "(41) 98765-4324",
            "crp": "08/456789",
            "bio": "Psicólogo clínico com especialização em trauma e TEPT. Abordagem integrativa combinando TCC e técnicas de processamento de trauma.",
            "experience_years": 15,
            "consultation_price": 300.0,
            "online_consultation": True,
            "in_person_consultation": True,
            "address": "Rua XV de Novembro, 100",
            "city": "Curitiba",
            "state": "PR",
            "zip_code": "80020-310",
            "specialty_ids": [5, 1],  # Trauma, Ansiedade
            "approach_ids": [1, 8],  # TCC, Integrativa
            "is_verified": True
        },
        {
            "email": "juliana.costa@lumine.com",
            "full_name": "Juliana Costa",
            "phone": "(51) 98765-4325",
            "crp": "07/567890",
            "bio": "Psicóloga especializada em autoestima e desenvolvimento pessoal. Abordagem humanista e gestalt. Atendo online.",
            "experience_years": 6,
            "consultation_price": 150.0,
            "online_consultation": True,
            "in_person_consultation": False,
            "address": "Av. Borges de Medeiros, 500",
            "city": "Porto Alegre",
            "state": "RS",
            "zip_code": "90020-020",
            "specialty_ids": [7],  # Autoestima
            "approach_ids": [3, 4],  # Humanista, Gestalt
            "is_verified": False
        },
        {
            "email": "roberto.almeida@lumine.com",
            "full_name": "Roberto Almeida",
            "phone": "(85) 98765-4326",
            "crp": "11/678901",
            "bio": "Psicólogo com formação em psicanálise. Especializado em depressão e luto. Atendo presencialmente em Fortaleza.",
            "experience_years": 20,
            "consultation_price": 280.0,
            "online_consultation": False,
            "in_person_consultation": True,
            "address": "Av. Beira Mar, 2000",
            "city": "Fortaleza",
            "state": "CE",
            "zip_code": "60165-121",
            "specialty_ids": [2, 8],  # Depressão, Luto
            "approach_ids": [2],  # Psicanálise
            "is_verified": True
        },
    ]
    
    psychologists = []
    for i, psych_data in enumerate(psychologists_data):
        # Criar usuário
        user = User(
            email=psych_data["email"],
            senha_hash=get_password_hash("senha123"),
            nome_completo=psych_data["full_name"],
            telefone=psych_data["phone"],
            eh_psicologo=True,
            esta_ativo=True,
            eh_admin=False
        )
        db.add(user)
        db.flush()
        
        # Criar perfil de psicólogo
        psychologist = Psychologist(
            id_usuario=user.id,
            crp=psych_data["crp"],
            biografia=psych_data["bio"],
            anos_experiencia=psych_data["experience_years"],
            preco_consulta=psych_data["consultation_price"],
            consulta_online=psych_data["online_consultation"],
            consulta_presencial=psych_data["in_person_consultation"],
            endereco=psych_data.get("address"),
            cidade=psych_data.get("city"),
            estado=psych_data.get("state"),
            cep=psych_data.get("zip_code"),
            esta_verificado=psych_data.get("is_verified", False),
            avaliacao=round(random.uniform(4.0, 5.0), 1),
            total_avaliacoes=random.randint(5, 50)
        )
        db.add(psychologist)
        db.flush()
        
        # Adicionar especialidades e abordagens
        for spec_id in psych_data["specialty_ids"]:
            specialty = specialties[spec_id - 1]
            psychologist.specialties.append(specialty)
        
        for app_id in psych_data["approach_ids"]:
            approach = approaches[app_id - 1]
            psychologist.approaches.append(approach)
        
        psychologists.append(psychologist)
    
    db.commit()
    print(f"[OK] {len(psychologists)} psicólogos criados")
    
    # ========== USUÁRIOS CLIENTES ==========
    print("[*] Criando usuários clientes...")
    clients_data = [
        {"email": "cliente1@teste.com", "full_name": "Pedro Alves", "phone": "(11) 91234-5678"},
        {"email": "cliente2@teste.com", "full_name": "Fernanda Lima", "phone": "(21) 92345-6789"},
        {"email": "cliente3@teste.com", "full_name": "Lucas Martins", "phone": "(31) 93456-7890"},
        {"email": "cliente4@teste.com", "full_name": "Beatriz Souza", "phone": "(41) 94567-8901"},
    ]
    
    clients = []
    for client_data in clients_data:
        user = User(
            email=client_data["email"],
            senha_hash=get_password_hash("senha123"),
            nome_completo=client_data["full_name"],
            telefone=client_data["phone"],
            eh_psicologo=False,
            esta_ativo=True,
            eh_admin=False
        )
        db.add(user)
        clients.append(user)
    
    db.commit()
    print(f"[OK] {len(clients)} clientes criados")
    
    # ========== AVALIAÇÕES ==========
    print("[*] Criando avaliações...")
    review_comments = [
        "Excelente profissional, muito atenciosa e competente!",
        "Me ajudou muito com minha ansiedade. Recomendo!",
        "Terapia muito produtiva, sinto grande evolução.",
        "Profissional qualificado e empático.",
        "Ótima experiência, já marquei mais consultas.",
        "Muito acolhedor e profissional.",
        "Abordagem diferente e eficaz.",
        "Recomendo para todos que precisam de ajuda.",
    ]
    
    reviews_created = 0
    for psychologist in psychologists:
        num_reviews = random.randint(3, 8)
        for _ in range(num_reviews):
            client = random.choice(clients)
            review = Review(
                id_psicologo=psychologist.id,
                id_usuario=client.id,
                avaliacao=random.randint(4, 5),
                comentario=random.choice(review_comments)
            )
            db.add(review)
            reviews_created += 1
    
    db.commit()
    print(f"[OK] {reviews_created} avaliações criadas")
    
    # Atualizar ratings dos psicólogos
    for psychologist in psychologists:
        avg_rating = db.query(func.avg(Review.avaliacao)).filter(
            Review.id_psicologo == psychologist.id
        ).scalar()
        total_reviews = db.query(func.count(Review.id)).filter(
            Review.id_psicologo == psychologist.id
        ).scalar()
        if avg_rating:
            psychologist.avaliacao = round(float(avg_rating), 1)
            psychologist.total_avaliacoes = total_reviews
    
    db.commit()
    
    # ========== AGENDAMENTOS ==========
    print("[*] Criando agendamentos...")
    appointments_created = 0
    for i in range(15):
        psychologist = random.choice(psychologists)
        client = random.choice(clients)
        appointment_date = datetime.now() + timedelta(days=random.randint(1, 30), hours=random.randint(9, 18))
        
        appointment = Appointment(
            id_psicologo=psychologist.id,
            id_usuario=client.id,
            data_agendamento=appointment_date,
            tipo_agendamento=random.choice(["online", "presencial"]),
            status=random.choice(["pending", "confirmed", "completed"]),
            observacoes=f"Consulta agendada para {appointment_date.strftime('%d/%m/%Y %H:%M')}"
        )
        db.add(appointment)
        appointments_created += 1
    
    db.commit()
    print(f"[OK] {appointments_created} agendamentos criados")
    
    # ========== PAGAMENTOS ==========
    print("[*] Criando pagamentos...")
    appointments = db.query(Appointment).filter(Appointment.status.in_(["confirmed", "completed"])).all()
    payments_created = 0
    
    for appointment in appointments[:10]:  # Pagar apenas alguns
        psychologist = db.query(Psychologist).filter(Psychologist.id == appointment.id_psicologo).first()
        if psychologist and psychologist.preco_consulta:
            payment = Payment(
                id_agendamento=appointment.id,
                id_usuario=appointment.id_usuario,
                valor=psychologist.preco_consulta,
                metodo_pagamento=random.choice(["credit_card", "debit_card", "pix"]),
                status="paid",
                id_pagamento=f"PAY-{random.randint(100000, 999999)}",
                id_transacao=f"TXN-{random.randint(100000, 999999)}"
            )
            db.add(payment)
            appointment.status_pagamento = "paid"
            payments_created += 1
    
    db.commit()
    print(f"[OK] {payments_created} pagamentos criados")
    
    # ========== HORÁRIOS DISPONÍVEIS ==========
    print("[*] Criando horários disponíveis...")
    days_of_week = list(range(7))  # 0=Segunda, 6=Domingo
    time_slots = [
        ("08:00", "12:00"),
        ("13:00", "17:00"),
        ("18:00", "21:00"),
    ]
    
    availability_created = 0
    for psychologist in psychologists:
        # Cada psicólogo tem disponibilidade em alguns dias da semana
        available_days = random.sample(days_of_week[:5], random.randint(3, 5))  # Segunda a Sexta
        for day in available_days:
            start_time, end_time = random.choice(time_slots)
            availability = PsychologistAvailability(
                id_psicologo=psychologist.id,
                dia_da_semana=day,
                horario_inicio=start_time,
                horario_fim=end_time,
                esta_disponivel=True
            )
            db.add(availability)
            availability_created += 1
    
    db.commit()
    print(f"[OK] {availability_created} horários disponíveis criados")
    
    # ========== POSTS DO FÓRUM ==========
    print("[*] Criando posts do fórum...")
    forum_posts_data = [
        {
            "title": "Como lidar com ansiedade no trabalho?",
            "content": "Estou passando por um momento difícil no trabalho e a ansiedade está me atrapalhando muito. Alguém tem dicas?",
            "category": "ansiedade",
            "is_anonymous": False
        },
        {
            "title": "Primeira consulta - o que esperar?",
            "content": "Vou fazer minha primeira consulta psicológica na próxima semana. Estou um pouco nervoso. O que devo esperar?",
            "category": "geral",
            "is_anonymous": True
        },
        {
            "title": "Terapia online funciona?",
            "content": "Alguém já fez terapia online? Funciona bem? Estou pensando em tentar.",
            "category": "geral",
            "is_anonymous": False
        },
        {
            "title": "Como ajudar alguém com depressão?",
            "content": "Minha amiga está passando por um momento difícil e acho que pode estar com depressão. Como posso ajudar?",
            "category": "depressao",
            "is_anonymous": False
        },
    ]
    
    posts_created = 0
    for post_data in forum_posts_data:
        author = random.choice(clients)
        post = ForumPost(
            id_usuario=author.id,
            titulo=post_data["title"],
            conteudo=post_data["content"],
            categoria=post_data["category"],
            eh_anonimo=post_data["is_anonymous"],
            visualizacoes=random.randint(10, 100),
            curtidas=random.randint(0, 20)
        )
        db.add(post)
        posts_created += 1
    
    db.commit()
    print(f"[OK] {posts_created} posts do fórum criados")
    
    # ========== COMENTÁRIOS DO FÓRUM ==========
    print("[*] Criando comentários do fórum...")
    posts = db.query(ForumPost).all()
    comments_created = 0
    
    for post in posts:
        num_comments = random.randint(2, 5)
        for _ in range(num_comments):
            commenter = random.choice(clients + [p.user for p in psychologists])
            comment = ForumComment(
                id_post=post.id,
                id_usuario=commenter.id,
                conteudo=random.choice([
                    "Obrigado por compartilhar! Isso me ajudou muito.",
                    "Também passo por isso, você não está sozinho.",
                    "Recomendo procurar ajuda profissional.",
                    "Excelente post, muito útil!",
                ]),
                eh_anonimo=random.choice([True, False]),
                curtidas=random.randint(0, 10)
            )
            db.add(comment)
            comments_created += 1
    
    db.commit()
    print(f"[OK] {comments_created} comentários criados")
    
    # ========== DIÁRIO DE EMOÇÕES ==========
    print("[*] Criando entradas do diário de emoções...")
    emotions = ["feliz", "triste", "ansioso", "irritado", "calmo", "estressado", "motivado", "cansado"]
    
    diary_entries_created = 0
    for client in clients:
        for i in range(random.randint(5, 15)):
            entry_date = datetime.now() - timedelta(days=random.randint(0, 30))
            entry = EmotionDiary(
                id_usuario=client.id,
                data=entry_date,
                emocao=random.choice(emotions),
                intensidade=random.randint(1, 10),
                notas=random.choice([
                    "Dia produtivo no trabalho",
                    "Sentindo-me um pouco sobrecarregado",
                    "Momento de reflexão importante",
                    "Conversa com amigos me ajudou",
                    None
                ]),
                tags=random.choice(["trabalho", "família", "saúde", "relacionamento", None])
            )
            db.add(entry)
            diary_entries_created += 1
    
    db.commit()
    print(f"[OK] {diary_entries_created} entradas do diário criadas")
    
    # ========== FAVORITOS ==========
    print("[*] Criando favoritos...")
    favorites_created = 0
    # Recarregar clientes na sessão para garantir que os relacionamentos estejam limpos
    for client in clients:
        db.refresh(client)
        num_favorites = random.randint(1, 3)
        favorite_psychologists = random.sample(psychologists, min(num_favorites, len(psychologists)))
        for psychologist in favorite_psychologists:
            # Verificar se o favorito já existe antes de adicionar (evita duplicatas)
            if psychologist not in client.favorite_psychologists:
                client.favorite_psychologists.append(psychologist)
                favorites_created += 1
    
    db.commit()
    print(f"[OK] {favorites_created} favoritos criados")
    
    # ========== ADMIN ==========
    print("[*] Verificando usuário administrador...")
    admin_email = "admin@lumine.com"
    existing_admin = db.query(User).filter(User.email == admin_email).first()
    if not existing_admin:
        admin_user = User(
            email=admin_email,
            senha_hash=get_password_hash("admin123"),
            nome_completo="Administrador",
            eh_admin=True,
            eh_psicologo=False,
            esta_ativo=True
        )
        db.add(admin_user)
        db.commit()
        print("[OK] Usuário administrador criado")
        print(f"   Email: {admin_email}")
        print(f"   Senha: admin123")
    else:
        print("[INFO] Usuário administrador já existe")
    
    print("\n" + "="*60)
    print("[OK] SEED DE DADOS CONCLUÍDO COM SUCESSO!")
    print("="*60)
    print(f"\n[*] Resumo:")
    print(f"   - {len(specialties)} especialidades")
    print(f"   - {len(approaches)} abordagens")
    print(f"   - {len(psychologists)} psicólogos")
    print(f"   - {len(clients)} clientes")
    print(f"   - {reviews_created} avaliações")
    print(f"   - {appointments_created} agendamentos")
    print(f"   - {payments_created} pagamentos")
    print(f"   - {availability_created} horários disponíveis")
    print(f"   - {posts_created} posts do fórum")
    print(f"   - {comments_created} comentários")
    print(f"   - {diary_entries_created} entradas do diário")
    print(f"   - {favorites_created} favoritos")
    print(f"\n[*] Credenciais de teste:")
    print(f"   Admin: admin@lumine.com / admin123")
    print(f"   Psicólogos: [email] / senha123")
    print(f"   Clientes: cliente[1-4]@teste.com / senha123")
    print("="*60)
    
except Exception as e:
    print(f"[ERRO] ERRO ao criar dados mockados: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

