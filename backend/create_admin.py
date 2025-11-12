"""
Script para criar um usuário administrador
Uso: python create_admin.py
"""
from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

def create_admin():
    db = SessionLocal()
    
    try:
        print("=" * 50)
        print("Criar Usuário Administrador")
        print("=" * 50)
        
        email = input("Email do administrador: ").strip()
        if not email:
            print("❌ Email é obrigatório!")
            return
        
        # Verificar se já existe
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"⚠️  Usuário com email {email} já existe!")
            response = input("Deseja torná-lo administrador? (s/n): ").strip().lower()
            if response == 's':
                existing.is_admin = True
                db.commit()
                print(f"✅ Usuário {email} agora é administrador!")
            else:
                print("Operação cancelada.")
            return
        
        password = input("Senha: ").strip()
        if not password:
            print("❌ Senha é obrigatória!")
            return
        
        full_name = input("Nome completo (ou Enter para 'Administrador'): ").strip()
        if not full_name:
            full_name = "Administrador"
        
        # Criar usuário admin
        admin_user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_admin=True,
            is_psychologist=False
        )
        
        db.add(admin_user)
        db.commit()
        
        print("\n" + "=" * 50)
        print("✅ Usuário administrador criado com sucesso!")
        print("=" * 50)
        print(f"Email: {email}")
        print(f"Nome: {full_name}")
        print(f"Senha: {password}")
        print("\n⚠️  IMPORTANTE: Guarde estas credenciais com segurança!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erro ao criar administrador: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

