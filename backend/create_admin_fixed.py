"""
Script para criar usuário administrador usando bcrypt corretamente
"""
import sys
import os

# Adicionar o diretório app ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User
import bcrypt

def create_admin():
    db = SessionLocal()
    
    try:
        admin_email = "admin@lumine.com"
        admin_password = "admin123"
        
        # Verificar se já existe
        existing = db.query(User).filter(User.email == admin_email).first()
        
        if existing:
            # Atualizar para admin e corrigir senha
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), salt)
            password_hash_str = password_hash.decode('utf-8')
            
            existing.is_admin = True
            existing.hashed_password = password_hash_str
            db.commit()
            print(f"Usuario {admin_email} atualizado para administrador")
            print(f"Email: {admin_email}")
            print(f"Senha: {admin_password}")
        else:
            # Criar hash usando bcrypt diretamente
            # bcrypt.hashpw retorna bytes, precisamos converter para string
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), salt)
            
            # Converter para string (formato que o passlib espera)
            # O passlib espera um hash bcrypt como string
            password_hash_str = password_hash.decode('utf-8')
            
            # Criar usuário
            admin_user = User(
                email=admin_email,
                hashed_password=password_hash_str,
                full_name="Administrador",
                is_admin=True,
                is_psychologist=False,
                is_active=True
            )
            
            db.add(admin_user)
            db.commit()
            
            print("SUCESSO: Usuario administrador criado!")
            print(f"Email: {admin_email}")
            print(f"Senha: {admin_password}")
            print("\nAgora voce pode fazer login como administrador.")
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

