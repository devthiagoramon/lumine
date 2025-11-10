# Guia Rápido de Instalação - Lumine

## 🚀 Início Rápido

### 1. Backend

```bash
# Navegue até a pasta do backend
cd backend

# Crie e ative o ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Configure o .env (copie do .env.example)
# Edite o arquivo .env com suas configurações

# Execute o seed para popular dados iniciais
python seed_data.py

# Inicie o servidor
python run.py
```

O backend estará rodando em: `http://localhost:8000`

### 2. Frontend

```bash
# Navegue até a pasta do frontend
cd frontend

# Instale as dependências
npm install

# Inicie o servidor de desenvolvimento
npm run dev
```

O frontend estará rodando em: `http://localhost:3000`

## 📝 Configuração do Banco de Dados

Por padrão, o sistema usa SQLite (não requer configuração adicional).

Para usar PostgreSQL:

1. Instale o PostgreSQL
2. Crie um banco de dados
3. Configure a URL no arquivo `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/lumine_db
   ```

## 🔑 Variáveis de Ambiente

Crie um arquivo `.env` na pasta `backend/` com:

```env
DATABASE_URL=sqlite:///./lumine.db
SECRET_KEY=sua-chave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Importante:** Altere o `SECRET_KEY` para uma chave segura em produção!

## ✅ Verificação

1. Acesse `http://localhost:3000` no navegador
2. Você deve ver a página inicial da Lumine
3. Teste criar uma conta
4. Teste fazer login
5. Se for psicólogo, crie um perfil profissional

## 🐛 Problemas Comuns

### Erro ao instalar dependências Python
- Certifique-se de ter Python 3.9+ instalado
- Use `python3` ao invés de `python` se necessário

### Erro ao instalar dependências Node
- Certifique-se de ter Node.js 18+ instalado
- Use `npm install --legacy-peer-deps` se houver conflitos

### Erro de conexão com o banco
- Verifique se o SQLite está funcionando (padrão)
- Se usar PostgreSQL, verifique se o serviço está rodando

### CORS Error
- Verifique se o backend está rodando na porta 8000
- Verifique se o frontend está rodando na porta 3000
- As URLs estão configuradas no `main.py` do backend

## 📚 Documentação da API

Após iniciar o backend, acesse:
- `http://localhost:8000/docs` - Documentação interativa (Swagger)
- `http://localhost:8000/redoc` - Documentação alternativa (ReDoc)

## 🎨 Recursos

- ✅ Sistema de autenticação completo
- ✅ Busca avançada de psicólogos
- ✅ Filtros múltiplos (especialidade, abordagem, localização, etc.)
- ✅ Perfis detalhados de psicólogos
- ✅ Dashboard para psicólogos
- ✅ Design responsivo e moderno
- ✅ Interface intuitiva

## 📞 Suporte

Para dúvidas ou problemas, consulte o README.md principal.

