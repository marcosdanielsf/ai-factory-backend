#!/usr/bin/env python3
"""
🚀 AI Factory Testing Framework - ONE-CLICK TEST
================================================
Script único que faz TUDO automaticamente.

Uso:
    python run_test.py
    
Isso é tudo! Ele vai:
1. Verificar conexão
2. Listar seus agentes
3. Te perguntar qual testar
4. Testar automaticamente
5. Mostrar resultado
"""

import os
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_env():
    """Verifica se .env está configurado"""
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print("❌ Configure suas credenciais primeiro!")
        print("\nOpção 1 - Criar arquivo .env:")
        print("  cp .env.example .env")
        print("  # Edite .env com suas credenciais\n")
        print("Opção 2 - Export direto:")
        print("  export SUPABASE_URL='https://xxx.supabase.co'")
        print("  export SUPABASE_KEY='eyJ...'\n")
        return False
    
    return True

def main():
    print_header("🏭 AI FACTORY V4 - QUICK TEST")
    
    # Check env
    if not check_env():
        sys.exit(1)
    
    # Import (só depois de verificar env)
    try:
        from supabase_client import SupabaseClient
    except ImportError:
        print("❌ Instale as dependências primeiro:")
        print("   pip install -r requirements.txt\n")
        sys.exit(1)
    
    # Connect
    print("🔄 Conectando ao Supabase...")
    try:
        supabase = SupabaseClient()
        print(f"✅ Conectado: {supabase.url[:30]}...\n")
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        sys.exit(1)
    
    # List agents
    print("📋 Seus agentes:\n")
    try:
        response = supabase.client.table('agent_versions')\
            .select('id, agent_name, version, status, is_active, validation_score')\
            .order('created_at', desc=True)\
            .limit(10)\
            .execute()
        
        agents = response.data
        
        if not agents:
            print("❌ Nenhum agente encontrado!")
            sys.exit(1)
        
        # Show agents
        for i, agent in enumerate(agents, 1):
            name = agent['agent_name'] or 'N/A'
            status = '✅' if agent['is_active'] else '❌'
            score = f"{agent['validation_score']:.1f}" if agent['validation_score'] else 'N/A'
            print(f"{i}. {name} v{agent['version']} {status} (Score: {score})")
        
        # Ask which to test
        print("\n" + "="*60)
        choice = input("\n👉 Qual agente testar? [1]: ").strip() or "1"
        
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(agents):
                print("❌ Número inválido!")
                sys.exit(1)
            
            selected = agents[idx]
            
        except ValueError:
            print("❌ Digite um número!")
            sys.exit(1)
        
        # Test agent
        print_header(f"🧪 TESTANDO: {selected['agent_name']}")
        
        agent_id = selected['id']
        
        # Load agent details
        print("1️⃣ Carregando agente...")
        agent = supabase.get_agent_version(agent_id)
        print(f"   ✅ {agent['agent_name']} v{agent['version']}")
        
        # Check skill
        print("\n2️⃣ Verificando skill...")
        skill = supabase.get_skill(agent_id)
        if skill:
            print(f"   ✅ Skill v{skill['version']} encontrado")
        else:
            print("   ⚠️  Sem skill (usará default)")
        
        # Mock test (por enquanto)
        print("\n3️⃣ Executando testes...")
        print("   ✅ Teste 1: Lead frio")
        print("   ✅ Teste 2: Pergunta preço")
        print("   ✅ Teste 3: Objeção")
        
        # Results
        print_header("📊 RESULTADOS")
        print("Overall Score: 8.5/10\n")
        print("Detalhes:")
        print("  • Completeness: 9.0/10")
        print("  • Tone: 8.5/10")
        print("  • Engagement: 8.0/10")
        print("  • Compliance: 9.5/10")
        print("  • Conversion: 7.5/10")
        
        print("\n✅ Teste concluído!")
        print("\n💡 NOTA: Este é um teste MOCK (simulado).")
        print("Para teste REAL com Claude Opus, implemente src/evaluator.py")
        print("Veja HANDOFF.md para detalhes.\n")
        
    except Exception as e:
        print(f"❌ Erro: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
