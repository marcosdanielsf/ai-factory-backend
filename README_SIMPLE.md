# 🚀 AI Factory Testing Framework - SUPER SIMPLES

## ⚡ Quick Start (3 minutos)

### 1. Setup

```bash
# Extrair ZIP
unzip ai-factory-testing-framework.zip
cd ai-factory-testing-framework

# Instalar (virtual env automático)
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar

```bash
# Opção A: Arquivo .env (recomendado)
cp .env.example .env
nano .env  # Cole suas credenciais

# Opção B: Export direto
export SUPABASE_URL='https://xxx.supabase.co'
export SUPABASE_KEY='eyJ...'
```

### 3. Testar

```bash
python run_test.py
```

**É SÓ ISSO!** 🎉

O script vai:
1. ✅ Verificar conexão
2. ✅ Mostrar seus agentes
3. ✅ Perguntar qual testar
4. ✅ Executar teste
5. ✅ Mostrar resultado

---

## 📋 Exemplo de Uso

```bash
$ python run_test.py

============================================================
  🏭 AI FACTORY V4 - QUICK TEST
============================================================

🔄 Conectando ao Supabase...
✅ Conectado: https://xxx.supabase.co...

📋 Seus agentes:

1. Isabella SDR v4 ✅ (Score: 8.7)
2. Assembly Line VSL v2 ✅ (Score: 7.9)
3. MOTIVE SQUAD v1 ❌ (Score: N/A)

============================================================

👉 Qual agente testar? [1]: 1

============================================================
  🧪 TESTANDO: Isabella SDR
============================================================

1️⃣ Carregando agente...
   ✅ Isabella SDR v4

2️⃣ Verificando skill...
   ✅ Skill v2 encontrado

3️⃣ Executando testes...
   ✅ Teste 1: Lead frio
   ✅ Teste 2: Pergunta preço
   ✅ Teste 3: Objeção

============================================================
  📊 RESULTADOS
============================================================

Overall Score: 8.5/10

Detalhes:
  • Completeness: 9.0/10
  • Tone: 8.5/10
  • Engagement: 8.0/10
  • Compliance: 9.5/10
  • Conversion: 7.5/10

✅ Teste concluído!
```

---

## 🎯 Outros Comandos (Opcional)

Se quiser mais controle:

```bash
# Ver todos os comandos disponíveis
python test_with_real_data.py --help

# Listar todos os agentes
python test_with_real_data.py --list-agents

# Ver detalhes de um agente específico
python test_with_real_data.py --agent-details <AGENT_ID>

# Verificar se migrations foram rodadas
python test_with_real_data.py --check-migrations
```

---

## 📚 Documentação

- **`QUICK_START.md`** - Guia detalhado
- **`HANDOFF.md`** - Para Claude Code implementar
- **`START_HERE.md`** - Resumo executivo

---

## 🐛 Problemas?

### "No module named 'supabase'"
```bash
pip install -r requirements.txt
```

### "SUPABASE_URL must be set"
```bash
# Configure .env ou export:
export SUPABASE_URL='...'
export SUPABASE_KEY='...'
```

---

## 🎉 Pronto!

Agora é só rodar:
```bash
python run_test.py
```

**Simples assim!** 🚀
