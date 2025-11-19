# 📚 Guia de Migrations e Seed Data - Lumine

Este guia explica como usar o sistema de migrations do Alembic e popular o banco de dados com dados mockados para testes.

## 🚀 Configuração Inicial

### 1. Instalar Dependências

Certifique-se de que todas as dependências estão instaladas:

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na pasta `backend/` com:

```env
DATABASE_URL=sqlite:///./lumine.db
SECRET_KEY=sua-chave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 📦 Executando Migrations

### Opção 1: Usar Alembic (Recomendado)

```bash
cd backend

# Verificar status das migrations
alembic current

# Aplicar todas as migrations pendentes
alembic upgrade head

# Reverter última migration
alembic downgrade -1

# Criar nova migration (após alterar models)
alembic revision --autogenerate -m "descrição da migration"
```

### Opção 2: Usar SQLAlchemy diretamente (Desenvolvimento)

O projeto também cria as tabelas automaticamente ao iniciar:

```bash
python run.py
```

Isso criará todas as tabelas automaticamente usando `Base.metadata.create_all()`.

## 🌱 Popular Dados Mockados

Após executar as migrations, você pode popular o banco com dados de teste:

```bash
cd backend
python migrations_seed_data.py
```

Este script criará:

- ✅ **10 Especialidades** (Ansiedade, Depressão, TDAH, etc.)
- ✅ **8 Abordagens** (TCC, Psicanálise, Humanista, etc.)
- ✅ **6 Psicólogos** com perfis completos
- ✅ **4 Clientes** para testes
- ✅ **Avaliações** para os psicólogos
- ✅ **Agendamentos** de exemplo
- ✅ **Pagamentos** mockados
- ✅ **Horários disponíveis** dos psicólogos
- ✅ **Posts e comentários** no fórum
- ✅ **Entradas** no diário de emoções
- ✅ **Favoritos** de psicólogos

## 🔑 Credenciais de Teste

Após executar o seed, você pode usar as seguintes credenciais:

### Administrador
- **Email:** `admin@lumine.com`
- **Senha:** `admin123`

### Psicólogos
- **Email:** `ana.silva@lumine.com` / **Senha:** `senha123`
- **Email:** `carlos.santos@lumine.com` / **Senha:** `senha123`
- **Email:** `maria.oliveira@lumine.com` / **Senha:** `senha123`
- **Email:** `joao.ferreira@lumine.com` / **Senha:** `senha123`
- **Email:** `juliana.costa@lumine.com` / **Senha:** `senha123`
- **Email:** `roberto.almeida@lumine.com` / **Senha:** `senha123`

### Clientes
- **Email:** `cliente1@teste.com` / **Senha:** `senha123`
- **Email:** `cliente2@teste.com` / **Senha:** `senha123`
- **Email:** `cliente3@teste.com` / **Senha:** `senha123`
- **Email:** `cliente4@teste.com` / **Senha:** `senha123`

## 📋 Estrutura das Migrations

```
backend/
├── alembic/
│   ├── env.py              # Configuração do Alembic
│   ├── script.py.mako      # Template para novas migrations
│   └── versions/
│       ├── 001_initial_migration.py    # Migration inicial
│       └── 002_seed_mock_data.py       # Dados básicos (especialidades/abordagens)
├── alembic.ini             # Configuração principal
└── migrations_seed_data.py # Script completo de seed
```

## 🔄 Workflow de Desenvolvimento

1. **Fazer alterações nos models** (`app/models.py`)
2. **Criar nova migration:**
   ```bash
   alembic revision --autogenerate -m "descrição"
   ```
3. **Revisar a migration gerada** em `alembic/versions/`
4. **Aplicar a migration:**
   ```bash
   alembic upgrade head
   ```
5. **Atualizar seed data** se necessário (`migrations_seed_data.py`)

## 🗄️ Estrutura do Banco de Dados

### Tabelas Principais

- `users` - Usuários do sistema (clientes, psicólogos, admins)
- `psychologists` - Perfis profissionais dos psicólogos
- `specialties` - Especialidades (Ansiedade, Depressão, etc.)
- `approaches` - Abordagens terapêuticas (TCC, Psicanálise, etc.)
- `reviews` - Avaliações dos psicólogos
- `appointments` - Agendamentos de consultas
- `payments` - Pagamentos das consultas
- `forum_posts` - Posts do fórum
- `forum_comments` - Comentários nos posts
- `emotion_diaries` - Entradas do diário de emoções
- `psychologist_availability` - Horários disponíveis dos psicólogos
- `favorites` - Psicólogos favoritos dos clientes

### Tabelas de Associação

- `psychologist_specialties` - Relação muitos-para-muitos
- `psychologist_approaches` - Relação muitos-para-muitos
- `favorites` - Relação muitos-para-muitos

## 🐛 Solução de Problemas

### Erro: "Table already exists"
Se as tabelas já existem, você pode:
1. Deletar o banco: `rm lumine.db` (SQLite) ou dropar o banco (PostgreSQL)
2. Ou usar: `alembic downgrade base` e depois `alembic upgrade head`

### Erro: "No such table"
Execute as migrations:
```bash
alembic upgrade head
```

### Resetar Banco de Dados
```bash
# SQLite
rm lumine.db
alembic upgrade head
python migrations_seed_data.py

# PostgreSQL
alembic downgrade base
alembic upgrade head
python migrations_seed_data.py
```

## 📝 Notas Importantes

- O script `migrations_seed_data.py` limpa todos os dados existentes (exceto admin) antes de inserir novos
- As senhas são hasheadas usando bcrypt
- Os dados são gerados aleatoriamente para simular um ambiente real
- O script pode ser executado múltiplas vezes sem problemas

## 🎯 Próximos Passos

Após popular os dados:
1. Inicie o servidor: `python run.py`
2. Acesse a documentação: `http://localhost:8000/docs`
3. Teste as rotas da API
4. Use as credenciais acima para fazer login no frontend

