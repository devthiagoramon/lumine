# Lumine - Plataforma de Conexão entre Pacientes e Psicólogos

Plataforma web responsiva e intuitiva que conecta pacientes com psicólogos qualificados, facilitando a busca por profissionais alinhados com necessidades específicas.

## 🚀 Tecnologias

### Backend
- **FastAPI** - Framework web moderno e rápido para Python
- **SQLAlchemy** - ORM para gerenciamento de banco de dados
- **PostgreSQL/SQLite** - Banco de dados
- **JWT** - Autenticação segura
- **Pydantic** - Validação de dados

### Frontend
- **React** - Biblioteca JavaScript para interfaces
- **Vite** - Build tool rápida
- **Tailwind CSS** - Framework CSS utilitário
- **React Router** - Roteamento
- **Axios** - Cliente HTTP
- **Lucide React** - Ícones modernos

## 📋 Pré-requisitos

- Python 3.9+
- Node.js 18+
- npm ou yarn
- PostgreSQL (opcional, pode usar SQLite)

## 🔧 Instalação

### Backend

1. Navegue até a pasta do backend:
```bash
cd backend
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Configure as variáveis de ambiente:
```bash
# Copie o arquivo .env.example para .env
cp .env.example .env

# Edite o .env com suas configurações
```

6. Execute o script de seed para popular dados iniciais:
```bash
python seed_data.py
```

7. Inicie o servidor:
```bash
python run.py
```

O backend estará rodando em `http://localhost:8000`

### Frontend

1. Navegue até a pasta do frontend:
```bash
cd frontend
```

2. Instale as dependências:
```bash
npm install
```

3. Inicie o servidor de desenvolvimento:
```bash
npm run dev
```

O frontend estará rodando em `http://localhost:3000`

## 📁 Estrutura do Projeto

```
Lumine/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Aplicação FastAPI principal
│   │   ├── database.py           # Configuração do banco de dados
│   │   ├── models.py             # Modelos SQLAlchemy
│   │   ├── schemas.py            # Schemas Pydantic
│   │   ├── auth.py               # Autenticação JWT
│   │   └── routers/              # Rotas da API
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── psychologists.py
│   │       └── search.py
│   ├── requirements.txt
│   ├── seed_data.py              # Script para popular dados iniciais
│   └── run.py                    # Script para iniciar o servidor
│
└── frontend/
    ├── src/
    │   ├── components/           # Componentes React reutilizáveis
    │   │   ├── Navbar.jsx
    │   │   ├── PsychologistCard.jsx
    │   │   └── PsychologistProfileForm.jsx
    │   ├── pages/                # Páginas da aplicação
    │   │   ├── Home.jsx
    │   │   ├── Search.jsx
    │   │   ├── Login.jsx
    │   │   ├── Register.jsx
    │   │   ├── PsychologistProfile.jsx
    │   │   └── Dashboard.jsx
    │   ├── contexts/              # Contextos React
    │   │   └── AuthContext.jsx
    │   ├── api/                   # Configuração da API
    │   │   └── axios.js
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css
    ├── package.json
    └── vite.config.js
```

## 🎯 Funcionalidades

### Para Pacientes
- ✅ Busca avançada de psicólogos com múltiplos filtros
- ✅ Visualização de perfis detalhados
- ✅ Filtros por especialidade, abordagem, localização
- ✅ Filtros por tipo de consulta (online/presencial)
- ✅ Filtros por avaliação e preço
- ✅ Sistema de autenticação

### Para Psicólogos
- ✅ Criação e edição de perfil profissional
- ✅ Cadastro de especialidades e abordagens
- ✅ Informações de contato e localização
- ✅ Definição de valores e tipos de consulta
- ✅ Dashboard personalizado

## 🔐 Autenticação

A aplicação utiliza JWT (JSON Web Tokens) para autenticação. Após o login, o token é armazenado no localStorage e incluído automaticamente nas requisições.

## 🎨 Design

O design foi criado com foco em:
- **Responsividade** - Funciona perfeitamente em desktop, tablet e mobile
- **Intuitividade** - Interface clara e fácil de usar
- **Acessibilidade** - Cores contrastantes e navegação clara
- **Modernidade** - Design atual com gradientes e animações suaves

## 📝 API Endpoints

### Autenticação
- `POST /api/auth/register` - Registrar novo usuário
- `POST /api/auth/login` - Fazer login
- `GET /api/auth/me` - Obter usuário atual

### Psicólogos
- `GET /api/psychologists/` - Listar psicólogos
- `GET /api/psychologists/{id}` - Obter psicólogo específico
- `GET /api/psychologists/me` - Obter perfil do psicólogo logado
- `POST /api/psychologists/` - Criar perfil de psicólogo
- `PUT /api/psychologists/me` - Atualizar perfil de psicólogo

### Busca
- `GET /api/search/psychologists` - Buscar psicólogos com filtros
- `GET /api/search/specialties` - Listar especialidades
- `GET /api/search/approaches` - Listar abordagens

## 🚀 Deploy

### Backend
Para produção, use um servidor ASGI como:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
Para build de produção:
```bash
npm run build
```

Os arquivos estarão em `dist/` e podem ser servidos por qualquer servidor estático.

## 📄 Licença

Este projeto foi desenvolvido para o MPS 2025.

## 👥 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📧 Contato

Para dúvidas ou sugestões, entre em contato através do repositório.

