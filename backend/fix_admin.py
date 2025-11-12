"""
Script para verificar e corrigir problemas com o campo is_admin
"""
import sqlite3
from app.database import SessionLocal, engine
from app.models import Base, User
from sqlalchemy import inspect

def check_and_fix_database():
    """Verifica se a coluna is_admin existe e cria se necessário"""
    
    # Verificar se é SQLite
    db_url = str(engine.url)
    if "sqlite" in db_url:
        db_path = db_url.replace("sqlite:///", "")
        print(f"Verificando banco SQLite: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a coluna is_admin existe
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if "is_admin" not in columns:
            print("AVISO: Coluna is_admin nao encontrada. Adicionando...")
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
                conn.commit()
                print("SUCESSO: Coluna is_admin adicionada com sucesso!")
            except Exception as e:
                print(f"ERRO ao adicionar coluna: {e}")
                conn.rollback()
        else:
            print("OK: Coluna is_admin ja existe")
        
        conn.close()
    else:
        print("AVISO: Banco nao e SQLite. Voce precisara criar uma migracao manualmente.")
        print("   Ou recriar as tabelas executando:")
        print("   python -c 'from app.database import Base, engine; Base.metadata.drop_all(engine); Base.metadata.create_all(engine)'")
    
    # Verificar usuários admin
    db = SessionLocal()
    try:
        admins = db.query(User).filter(User.is_admin == True).all()
        if admins:
            print(f"\nOK: Encontrados {len(admins)} usuario(s) administrador(es):")
            for admin in admins:
                print(f"   - {admin.email} ({admin.full_name})")
        else:
            print("\nAVISO: Nenhum usuario administrador encontrado!")
            print("   Execute: python seed_data.py ou python create_admin.py")
        
        # Verificar todos os usuários
        all_users = db.query(User).all()
        print(f"\nTotal de usuarios no banco: {len(all_users)}")
        
    except Exception as e:
        print(f"ERRO ao verificar usuarios: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Verificação e Correção do Banco de Dados")
    print("=" * 60)
    check_and_fix_database()
    print("=" * 60)

