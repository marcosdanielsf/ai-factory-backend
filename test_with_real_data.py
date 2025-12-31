#!/usr/bin/env python3
"""
Quick Test Script - AI Factory Testing Framework
================================================
Testa o framework com dados REAIS do seu Supabase.

Usage:
    python test_with_real_data.py --list-agents
    python test_with_real_data.py --test-agent <AGENT_ID>
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from supabase_client import SupabaseClient


def print_separator(title: str = ""):
    """Print visual separator"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    else:
        print(f"{'='*60}\n")


def list_all_agents(supabase: SupabaseClient):
    """
    Lista todos os agentes do Supabase
    (equivalente ao SQL query que você mandou)
    """
    print_separator("📋 LISTANDO TODOS OS AGENTES")
    
    try:
        # Query direto (equivalente ao seu SQL)
        response = supabase.client.table('agent_versions')\
            .select('id, agent_name, version, status, is_active, location_id, validation_score, created_at')\
            .order('created_at', desc=True)\
            .execute()
        
        agents = response.data
        
        if not agents:
            print("❌ Nenhum agente encontrado!")
            return
        
        print(f"✅ Encontrados {len(agents)} agentes:\n")
        
        # Tabela formatada
        print(f"{'ID':<38} {'Nome':<30} {'Ver':<5} {'Status':<15} {'Ativo':<7} {'Score':<7}")
        print("-" * 120)
        
        for agent in agents:
            agent_id = agent['id'][:36]
            name = (agent['agent_name'] or 'N/A')[:28]
            version = str(agent['version'] or 'N/A')
            status = (agent['status'] or 'N/A')[:13]
            is_active = '✅' if agent['is_active'] else '❌'
            score = f"{agent['validation_score']:.1f}" if agent['validation_score'] else 'N/A'
            
            print(f"{agent_id} {name:<30} v{version:<4} {status:<15} {is_active:<7} {score:<7}")
        
        print("\n")
        
        # Estatísticas
        active_count = sum(1 for a in agents if a['is_active'])
        with_score = sum(1 for a in agents if a['validation_score'])
        avg_score = sum(a['validation_score'] for a in agents if a['validation_score']) / with_score if with_score > 0 else 0
        
        print(f"📊 Estatísticas:")
        print(f"   Total: {len(agents)}")
        print(f"   Ativos: {active_count}")
        print(f"   Com score: {with_score}")
        print(f"   Score médio: {avg_score:.2f}/10")
        
        return agents
        
    except Exception as e:
        logger.error(f"Erro ao listar agentes: {e}")
        print(f"❌ Erro: {e}")
        return None


def get_agent_details(supabase: SupabaseClient, agent_id: str):
    """
    Mostra detalhes completos de um agente específico
    """
    print_separator(f"🔍 DETALHES DO AGENTE: {agent_id}")
    
    try:
        agent = supabase.get_agent_version(agent_id)
        
        if not agent:
            print(f"❌ Agente {agent_id} não encontrado!")
            return None
        
        # Informações básicas
        print(f"📝 Informações Básicas:")
        print(f"   ID: {agent['id']}")
        print(f"   Nome: {agent['agent_name']}")
        print(f"   Versão: v{agent['version']}")
        print(f"   Status: {agent['status']}")
        print(f"   Ativo: {'✅ Sim' if agent['is_active'] else '❌ Não'}")
        print(f"   Location ID: {agent['location_id']}")
        
        # Scores de validação
        print(f"\n📊 Validação:")
        print(f"   Status: {agent['validation_status'] or 'N/A'}")
        print(f"   Score: {agent['validation_score'] or 'N/A'}/10")
        
        # Datas
        print(f"\n📅 Datas:")
        print(f"   Criado: {agent['created_at']}")
        print(f"   Atualizado: {agent['updated_at']}")
        if agent.get('validated_at'):
            print(f"   Validado: {agent['validated_at']}")
        if agent.get('activated_at'):
            print(f"   Ativado: {agent['activated_at']}")
        
        # System prompt (preview)
        if agent.get('system_prompt'):
            prompt_preview = agent['system_prompt'][:200] + "..." if len(agent['system_prompt']) > 200 else agent['system_prompt']
            print(f"\n📜 System Prompt (preview):")
            print(f"   {prompt_preview}")
        
        # Agent config (se existir)
        if agent.get('agent_config'):
            config = agent['agent_config']
            print(f"\n⚙️ Configuração:")
            if 'modos_identificados' in config:
                print(f"   Modos: {', '.join(config['modos_identificados'])}")
            if 'hyperpersonalization' in config:
                hp = config['hyperpersonalization']
                print(f"   DDD: {hp.get('ddd', 'N/A')}")
                print(f"   Setor: {hp.get('setor', 'N/A')}")
        
        return agent
        
    except Exception as e:
        logger.error(f"Erro ao buscar agente: {e}")
        print(f"❌ Erro: {e}")
        return None


def test_agent_simulation(supabase: SupabaseClient, agent_id: str):
    """
    Simula um teste básico no agente
    (versão simplificada, sem Claude Opus ainda)
    """
    print_separator(f"🧪 SIMULANDO TESTE: {agent_id}")
    
    try:
        # 1. Buscar agente
        agent = supabase.get_agent_version(agent_id)
        if not agent:
            print(f"❌ Agente não encontrado!")
            return
        
        print(f"✅ Agente carregado: {agent['agent_name']} v{agent['version']}")
        
        # 2. Verificar se tem skill
        skill = supabase.get_skill(agent_id)
        if skill:
            print(f"✅ Skill encontrado: v{skill['version']}")
        else:
            print(f"⚠️  Nenhum skill encontrado (usará default)")
        
        # 3. Simular casos de teste
        print(f"\n🎯 Casos de Teste:")
        test_cases = [
            {"name": "Lead frio", "input": "Oi"},
            {"name": "Pergunta preço", "input": "Quanto custa?"},
            {"name": "Objeção", "input": "Tá muito caro"}
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"   {i}. {case['name']}: '{case['input']}'")
        
        # 4. Mock do resultado (sem rodar Claude ainda)
        print(f"\n📊 Resultado (SIMULADO):")
        print(f"   Overall Score: 8.5/10")
        print(f"   Completeness: 9.0/10")
        print(f"   Tone: 8.5/10")
        print(f"   Engagement: 8.0/10")
        print(f"   Compliance: 9.5/10")
        print(f"   Conversion: 7.5/10")
        
        print(f"\n✅ Teste simulado com sucesso!")
        print(f"\n💡 PRÓXIMO PASSO:")
        print(f"   Implementar src/evaluator.py para avaliação real com Claude Opus")
        
    except Exception as e:
        logger.error(f"Erro no teste: {e}")
        print(f"❌ Erro: {e}")


def check_new_columns(supabase: SupabaseClient):
    """
    Verifica se as novas colunas do framework existem
    (se migrations foram rodadas)
    """
    print_separator("🔍 VERIFICANDO MIGRATIONS")
    
    try:
        # Tenta buscar um agente com as novas colunas
        response = supabase.client.table('agent_versions')\
            .select('id, last_test_score, last_test_at, framework_approved')\
            .limit(1)\
            .execute()
        
        if response.data:
            agent = response.data[0]
            print("✅ Migrations rodadas com sucesso!")
            print(f"\n📊 Novas colunas disponíveis:")
            print(f"   - last_test_score: {'✅' if 'last_test_score' in agent else '❌'}")
            print(f"   - last_test_at: {'✅' if 'last_test_at' in agent else '❌'}")
            print(f"   - framework_approved: {'✅' if 'framework_approved' in agent else '❌'}")
            return True
        else:
            print("⚠️  Nenhum agente encontrado para verificar")
            return False
            
    except Exception as e:
        print("❌ Migrations NÃO foram rodadas ainda!")
        print(f"\n⚠️  Erro: {e}")
        print(f"\n💡 RODE AS MIGRATIONS PRIMEIRO:")
        print(f"   psql $DATABASE_URL -f migrations/001_add_testing_columns_to_agent_versions.sql")
        return False


def check_new_tables(supabase: SupabaseClient):
    """
    Verifica se as novas tabelas existem
    """
    print_separator("🔍 VERIFICANDO NOVAS TABELAS")
    
    tables_to_check = [
        'agenttest_test_results',
        'agenttest_skills'
    ]
    
    for table in tables_to_check:
        try:
            response = supabase.client.table(table).select('id').limit(1).execute()
            print(f"   ✅ {table}")
        except Exception as e:
            print(f"   ❌ {table} - {str(e)[:50]}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Test AI Factory Framework with Real Data'
    )
    parser.add_argument(
        '--list-agents',
        action='store_true',
        help='Lista todos os agentes'
    )
    parser.add_argument(
        '--agent-details',
        type=str,
        metavar='AGENT_ID',
        help='Mostra detalhes de um agente específico'
    )
    parser.add_argument(
        '--test-agent',
        type=str,
        metavar='AGENT_ID',
        help='Simula teste em um agente'
    )
    parser.add_argument(
        '--check-migrations',
        action='store_true',
        help='Verifica se migrations foram rodadas'
    )
    parser.add_argument(
        '--check-tables',
        action='store_true',
        help='Verifica se novas tabelas existem'
    )
    
    args = parser.parse_args()
    
    # Banner
    print_separator("🏭 AI FACTORY V4 - TESTING FRAMEWORK")
    print("Quick Test Script\n")
    
    # Check environment
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
        print("❌ ERRO: Variáveis de ambiente não configuradas!")
        print("\n💡 Configure:")
        print("   export SUPABASE_URL='https://xxx.supabase.co'")
        print("   export SUPABASE_KEY='eyJ...'")
        sys.exit(1)
    
    # Initialize Supabase client
    try:
        supabase = SupabaseClient()
        print(f"✅ Conectado ao Supabase: {supabase.url}\n")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        sys.exit(1)
    
    # Execute commands
    if args.check_migrations:
        check_new_columns(supabase)
    
    elif args.check_tables:
        check_new_tables(supabase)
    
    elif args.list_agents:
        list_all_agents(supabase)
    
    elif args.agent_details:
        get_agent_details(supabase, args.agent_details)
    
    elif args.test_agent:
        test_agent_simulation(supabase, args.test_agent)
    
    else:
        parser.print_help()
        print("\n💡 Exemplos de uso:")
        print("   python test_with_real_data.py --list-agents")
        print("   python test_with_real_data.py --agent-details <UUID>")
        print("   python test_with_real_data.py --test-agent <UUID>")
        print("   python test_with_real_data.py --check-migrations")


if __name__ == '__main__':
    main()
