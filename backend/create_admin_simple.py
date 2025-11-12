"""
Script simples para criar usuário administrador
Usa SQL direto para evitar problemas com bcrypt
"""
import sqlite3
import hashlib
import os

# Caminho do banco
db_path = "./lumine.db"

if not os.path.exists(db_path):
    print(f"ERRO: Banco de dados {db_path} nao encontrado!")
    print("Execute primeiro: python seed_data.py")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar se a coluna is_admin existe
cursor.execute("PRAGMA table_info(users)")
columns = [column[1] for column in cursor.fetchall()]

if "is_admin" not in columns:
    print("Adicionando coluna is_admin...")
    cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
    conn.commit()

# Criar usuário admin
admin_email = "admin@lumine.com"
admin_password = "admin123"

# Verificar se já existe
cursor.execute("SELECT id FROM users WHERE email = ?", (admin_email,))
existing = cursor.fetchone()

if existing:
    # Atualizar para admin
    cursor.execute("UPDATE users SET is_admin = 1 WHERE email = ?", (admin_email,))
    print(f"Usuario {admin_email} atualizado para administrador")
else:
    # Criar novo admin
    # Hash simples (não recomendado para produção, mas funciona para desenvolvimento)
    # Em produção, use bcrypt corretamente
    password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
    
    # Para compatibilidade com passlib, vamos usar um hash bcrypt manual
    # Mas como há problema, vamos criar com hash SHA256 temporário
    # O sistema vai precisar ser ajustado ou vamos usar o hash do passlib diretamente
    
    # Vamos tentar usar o passlib de forma diferente
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash(admin_password)
    except:
        # Fallback: usar SHA256 (não seguro, mas funciona para desenvolvimento)
        print("AVISO: Usando hash SHA256 (nao seguro para producao)")
        password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
    
    cursor.execute("""
        INSERT INTO users (email, hashed_password, full_name, is_admin, is_psychologist, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (admin_email, password_hash, "Administrador", 1, 0, 1))
    
    print(f"Usuario administrador criado!")
    print(f"Email: {admin_email}")
    print(f"Senha: {admin_password}")

conn.commit()
conn.close()

print("\nSUCESSO! Agora voce pode fazer login como administrador.")

