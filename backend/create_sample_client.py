"""
Script para criar um cliente de exemplo para teste
"""
from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

def create_sample_client():
    db = SessionLocal()
    
    try:
        print("=" * 50)
        print("Criar Cliente de Exemplo")
        print("=" * 50)
        
        # Cliente de exemplo
        client_email = "cliente@example.com"
        client_password = "senha123"
        client_name = "Cliente Exemplo"
        
        # Verificar se já existe
        existing = db.query(User).filter(User.email == client_email).first()
        if existing:
            print(f"Usuario {client_email} ja existe!")
            print(f"Email: {client_email}")
            print(f"Senha: {client_password}")
            print("\nVoce pode usar essas credenciais para fazer login.")
            return
        
        # Criar cliente
        client = User(
            email=client_email,
            hashed_password=get_password_hash(client_password),
            full_name=client_name,
            is_psychologist=False,
            is_admin=False,
            is_active=True
        )
        
        db.add(client)
        db.commit()
        
        print("\n" + "=" * 50)
        print("SUCESSO: Cliente criado com sucesso!")
        print("=" * 50)
        print(f"Email: {client_email}")
        print(f"Senha: {client_password}")
        print(f"Nome: {client_name}")
        print("\nAgora voce pode fazer login como cliente no frontend!")
        print("=" * 50)
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_client()

