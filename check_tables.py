#!/usr/bin/env python3
"""
Script para verificar se as tabelas necessárias existem no Supabase
via backend Railway
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

print("=" * 70)
print("VERIFICAÇÃO DE TABELAS - AI FACTORY V4")
print("=" * 70)
print()

# Importar Supabase Client
try:
    from src.supabase_client import SupabaseClient
    supabase_client = SupabaseClient()
    print(f"✅ Conectado ao Supabase: {supabase_client.url}")
    print()
except Exception as e:
    print(f"❌ Erro ao conectar no Supabase: {e}")
    sys.exit(1)

# Tabelas que devem existir
REQUIRED_TABLES = [
    'agent_versions',
    'agent_metrics',
    'agent_conversations',
    'agent_conversation_messages'
]

print("VERIFICANDO TABELAS:")
print("-" * 70)

results = []

for table_name in REQUIRED_TABLES:
    try:
        # Tentar buscar 1 registro da tabela
        response = supabase_client.client.from_(table_name).select('*').limit(1).execute()

        # Se não deu erro, a tabela existe
        count = len(response.data)
        print(f"✅ {table_name:<35} | Existe | {count} registro(s) de exemplo")
        results.append((table_name, True, count))

    except Exception as e:
        error_msg = str(e)

        # Se erro é "relation does not exist", tabela não existe
        if 'does not exist' in error_msg or 'relation' in error_msg:
            print(f"❌ {table_name:<35} | NÃO EXISTE")
            results.append((table_name, False, error_msg))
        else:
            print(f"⚠️  {table_name:<35} | ERRO: {error_msg[:50]}...")
            results.append((table_name, False, error_msg))

print()
print("=" * 70)
print("RESUMO")
print("=" * 70)

existing = [r for r in results if r[1]]
missing = [r for r in results if not r[1]]

print(f"✅ Tabelas encontradas: {len(existing)}/{len(REQUIRED_TABLES)}")
print(f"❌ Tabelas faltando: {len(missing)}/{len(REQUIRED_TABLES)}")
print()

if missing:
    print("⚠️  ATENÇÃO: Tabelas faltando:")
    for table, _, error in missing:
        print(f"   - {table}")
    print()
    print("PRÓXIMO PASSO: Executar migrations SQL para criar as tabelas")
    print("Arquivo: /supabase/migrations/xxx_create_tables.sql")
    sys.exit(1)
else:
    print("🎉 Todas as tabelas necessárias existem!")
    sys.exit(0)
