#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent / 'src'))

def main():
    print("\n" + "="*60)
    print("  🏭 AI FACTORY V4 - QUICK TEST")
    print("="*60 + "\n")
    
    from supabase_client import SupabaseClient
    
    supabase = SupabaseClient()
    print(f"✅ Conectado: {supabase.url[:30]}...\n")
    
    # Lista agentes (simplificado)
    print("📋 Seus agentes:\n")
    response = supabase.client.table('agent_versions')\
        .select('id, agent_name, version, status, is_active, validation_score')\
        .order('created_at', desc=True)\
        .limit(10)\
        .execute()
    
    agents = response.data
    
    for i, agent in enumerate(agents, 1):
        name = agent['agent_name'] or 'N/A'
        status = '✅' if agent['is_active'] else '❌'
        score = f"{agent['validation_score']:.1f}" if agent['validation_score'] else 'N/A'
        print(f"{i}. {name} v{agent['version']} {status} (Score: {score})")
    
    print("\n" + "="*60)
    choice = input("\n👉 Qual agente testar? [1]: ").strip() or "1"
    idx = int(choice) - 1
    selected = agents[idx]
    
    print("\n" + "="*60)
    print(f"  🧪 TESTANDO: {selected['agent_name']}")
    print("="*60 + "\n")
    
    # Buscar agente (SEM JOINS)
    print("1️⃣ Carregando agente...")
    agent_detail = supabase.client.table('agent_versions')\
        .select('*')\
        .eq('id', selected['id'])\
        .single()\
        .execute()
    
    agent = agent_detail.data
    print(f"   ✅ {agent['agent_name']} v{agent['version']}")
    
    # Mock teste
    print("\n2️⃣ Executando testes...")
    print("   ✅ Teste 1: Lead frio")
    print("   ✅ Teste 2: Pergunta preço")
    print("   ✅ Teste 3: Objeção")
    
    print("\n" + "="*60)
    print("  📊 RESULTADOS (SIMULADO)")
    print("="*60 + "\n")
    print("Overall Score: 8.5/10\n")
    print("Detalhes:")
    print("  • Completeness: 9.0/10")
    print("  • Tone: 8.5/10")
    print("  • Engagement: 8.0/10")
    print("  • Compliance: 9.5/10")
    print("  • Conversion: 7.5/10")
    print("\n✅ Teste concluído!\n")

if __name__ == '__main__':
    main()

