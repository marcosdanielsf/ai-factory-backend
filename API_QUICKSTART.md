# API Quick Start Guide

## 🚀 Inicialização Rápida

### 1. Configurar Environment Variables

```bash
cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework/
cp .env.example .env
nano .env  # Editar com suas credenciais
```

Variáveis obrigatórias:
- `SUPABASE_URL` - URL do seu projeto Supabase
- `SUPABASE_KEY` - Anon key do Supabase
- `ANTHROPIC_API_KEY` - Sua chave da Anthropic
- `API_KEY` - Chave secreta para autenticar requests

### 2. Ativar Virtual Environment

```bash
source venv/bin/activate
```

### 3. Instalar Dependências (se necessário)

```bash
pip install -r requirements.txt
```

### 4. Iniciar o Servidor

```bash
# Modo desenvolvimento (hot reload)
python server.py

# OU via uvicorn direto
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Produção (Gunicorn)
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker
```

Servidor rodando em: **http://localhost:8000**

### 5. Acessar Documentação Interativa

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📋 Endpoints Disponíveis

### Health Check
```bash
curl http://localhost:8000/health
```

### 1. Listar Agentes
```bash
curl -X GET "http://localhost:8000/api/agents?limit=10" \
  -H "X-API-Key: your-secret-api-key-here-change-me"
```

### 2. Detalhes de um Agente
```bash
curl -X GET "http://localhost:8000/api/agent/{AGENT_UUID}" \
  -H "X-API-Key: your-secret-api-key-here-change-me"
```

### 3. Enfileirar Teste
```bash
curl -X POST "http://localhost:8000/api/test-agent" \
  -H "X-API-Key: your-secret-api-key-here-change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_version_id": "UUID_DO_AGENTE"
  }'
```

Retorna:
```json
{
  "status": "queued",
  "agent_id": "UUID",
  "message": "Test queued for agent..."
}
```

O teste roda em **background**. Verifique o status em:
```bash
curl -X GET "http://localhost:8000/api/agent/{AGENT_UUID}" \
  -H "X-API-Key: your-key"
```

### 4. Histórico de Testes
```bash
curl -X GET "http://localhost:8000/api/agent/{AGENT_UUID}/tests?limit=20" \
  -H "X-API-Key: your-key"
```

### 5. Detalhes de um Teste Específico
```bash
curl -X GET "http://localhost:8000/api/test-results/{TEST_ID}" \
  -H "X-API-Key: your-key"
```

### 6. Buscar Skill de um Agente
```bash
curl -X GET "http://localhost:8000/api/agent/{AGENT_UUID}/skill" \
  -H "X-API-Key: your-key"
```

### 7. Criar/Atualizar Skill
```bash
curl -X POST "http://localhost:8000/api/agent/{AGENT_UUID}/skill" \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "instructions": "# Isabella SDR Agent\n\nYou are a sales development representative...",
    "examples": "Example 1: ...",
    "rubric": "1. Completeness (25%)\n2. Tone (20%)...",
    "test_cases": [
      {
        "name": "Cold lead - first message",
        "input": "Hi",
        "expected_behavior": "Friendly greeting + open question"
      }
    ],
    "local_file_path": "./skills/isabella-sdr/"
  }'
```

---

## 🧪 Testar Todos os Endpoints

```bash
# Script de teste automatizado
./test_api.sh
```

Antes de rodar, edite `test_api.sh` e substitua:
- `API_KEY` pela sua chave
- `AGENT_UUID` por um UUID real do banco

---

## 🔐 Autenticação

**Todas as rotas (exceto `/health`) requerem autenticação via header:**

```
X-API-Key: your-secret-api-key-here-change-me
```

Erro sem API Key:
```json
{
  "error": true,
  "detail": "Missing API Key. Include 'X-API-Key' header.",
  "timestamp": "2024-12-31T10:00:00"
}
```

Erro com API Key inválida:
```json
{
  "error": true,
  "detail": "Invalid API Key",
  "timestamp": "2024-12-31T10:00:00"
}
```

---

## 🔧 Configuração Avançada

### CORS

Edite em `.env`:
```
CORS_ORIGINS=http://localhost:3000,https://app.mottivme.com
```

### Rate Limiting

Por padrão: **100 requests/minuto por IP**

Edite em `config.yaml`:
```yaml
server:
  rate_limit_enabled: true
  rate_limit_requests: 100
  rate_limit_period_seconds: 60
```

---

## 📊 Workflow Completo de Teste

```bash
# 1. Listar agentes disponíveis
AGENTS=$(curl -s "http://localhost:8000/api/agents?limit=5" \
  -H "X-API-Key: $API_KEY")
echo $AGENTS | python3 -m json.tool

# 2. Pegar ID do primeiro agente
AGENT_ID=$(echo $AGENTS | python3 -c "import sys, json; print(json.load(sys.stdin)[0]['id'])")

# 3. Enfileirar teste
curl -X POST "http://localhost:8000/api/test-agent" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"agent_version_id\": \"$AGENT_ID\"}"

# 4. Aguardar alguns segundos (teste roda em background)
sleep 30

# 5. Verificar resultado
curl -s "http://localhost:8000/api/agent/$AGENT_ID" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool

# 6. Ver histórico completo
curl -s "http://localhost:8000/api/agent/$AGENT_ID/tests" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool
```

---

## 🐛 Troubleshooting

### Erro: "Supabase not initialized"
- Verifique se `.env` está configurado corretamente
- Teste conexão: `python -c "from src.supabase_client import SupabaseClient; c = SupabaseClient(); print('OK')"`

### Erro: "Module not found"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Servidor não inicia
```bash
# Verifique se a porta está livre
lsof -ti:8000 | xargs kill -9  # Mata processo na porta 8000
python server.py
```

### CORS Error no Browser
Adicione seu domínio em `.env`:
```
CORS_ORIGINS=http://localhost:3000,https://seu-dominio.com
```

---

## 📝 Próximos Passos

1. ✅ Configure `.env` com credenciais reais
2. ✅ Rode `python server.py`
3. ✅ Acesse http://localhost:8000/docs
4. ✅ Teste com `./test_api.sh`
5. ✅ Integre com N8N/front-end

---

**Documentação completa:** `/docs` ou `/redoc` quando servidor estiver rodando.
