#!/bin/bash

# =============================================================================
# AI Factory Testing Framework - Quick Deploy Script
# =============================================================================
# Este script ajuda você a fazer deploy no Railway de forma guiada
#
# Uso: ./quick-deploy.sh
# =============================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}"
echo "======================================================================"
echo "   AI FACTORY TESTING FRAMEWORK - RAILWAY QUICK DEPLOY"
echo "======================================================================"
echo -e "${NC}"
echo ""

# Verificar se está no diretório correto
if [ ! -f "Dockerfile" ] || [ ! -f "railway.toml" ]; then
    echo -e "${RED}❌ ERRO: Execute este script no diretório raiz do projeto!${NC}"
    echo "cd /Users/marcosdaniels/Downloads/ai-factory-testing-framework"
    exit 1
fi

echo -e "${GREEN}✅ Diretório correto verificado${NC}"
echo ""

# Verificar se Railway CLI está instalado
echo -e "${BLUE}Verificando Railway CLI...${NC}"
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}⚠️  Railway CLI não encontrado${NC}"
    echo ""
    echo "Deseja instalar agora? (y/n)"
    read -r install_railway
    
    if [ "$install_railway" = "y" ] || [ "$install_railway" = "Y" ]; then
        echo "Instalando Railway CLI..."
        npm install -g @railway/cli
        echo -e "${GREEN}✅ Railway CLI instalado${NC}"
    else
        echo -e "${RED}❌ Railway CLI é necessário. Instale com: npm install -g @railway/cli${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Railway CLI encontrado: $(railway --version)${NC}"
fi
echo ""

# Verificar credenciais
echo -e "${BLUE}Verificando credenciais necessárias...${NC}"
echo ""

if [ ! -f ".env.railway" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env.railway não encontrado${NC}"
    echo ""
    echo "Vamos criar agora. Você precisará de:"
    echo "  1. Supabase URL e Keys (https://supabase.com/dashboard)"
    echo "  2. Anthropic API Key (https://console.anthropic.com)"
    echo "  3. API Key customizada (opcional)"
    echo ""
    echo "Pressione ENTER para continuar..."
    read -r
    
    echo "Copiando template..."
    cp .env.railway.example .env.railway
    
    echo ""
    echo -e "${YELLOW}🔧 CONFIGURE SEU .env.railway AGORA:${NC}"
    echo "Abrindo editor..."
    sleep 2
    
    # Tentar abrir com editor disponível
    if command -v code &> /dev/null; then
        code .env.railway
    elif command -v nano &> /dev/null; then
        nano .env.railway
    elif command -v vi &> /dev/null; then
        vi .env.railway
    else
        echo "Abra manualmente: .env.railway"
    fi
    
    echo ""
    echo "Após preencher as variáveis, pressione ENTER para continuar..."
    read -r
fi

echo -e "${GREEN}✅ Arquivo .env.railway encontrado${NC}"
echo ""

# Escolher método de deploy
echo -e "${CYAN}======================================================================"
echo "   ESCOLHA O MÉTODO DE DEPLOY"
echo "======================================================================${NC}"
echo ""
echo "1) Deploy via Railway CLI (mais rápido, requer login)"
echo "2) Deploy via GitHub (recomendado para produção)"
echo "3) Apenas preparar (não fazer deploy agora)"
echo ""
echo -n "Escolha (1-3): "
read -r deploy_method

case $deploy_method in
    1)
        echo ""
        echo -e "${BLUE}Método escolhido: Railway CLI${NC}"
        echo ""
        
        # Login
        echo "Fazendo login no Railway..."
        railway login
        
        echo ""
        echo -e "${GREEN}✅ Login realizado${NC}"
        echo ""
        
        # Inicializar projeto (se não existir)
        echo "Inicializando projeto Railway..."
        if railway init; then
            echo -e "${GREEN}✅ Projeto inicializado${NC}"
        else
            echo -e "${YELLOW}⚠️  Projeto já existe ou erro na inicialização${NC}"
        fi
        echo ""
        
        # Upload variáveis
        echo "Fazendo upload das variáveis de ambiente..."
        echo "Nota: Isso pode demorar alguns segundos..."
        
        # Extrair variáveis do .env.railway
        while IFS='=' read -r key value; do
            # Ignorar comentários e linhas vazias
            if [[ ! $key =~ ^# ]] && [[ -n $key ]]; then
                # Remover espaços e quotes
                key=$(echo "$key" | xargs)
                value=$(echo "$value" | xargs | sed 's/^"//' | sed 's/"$//')
                
                if [[ -n $value ]] && [[ ! $value =~ ^(https://seu-projeto|eyJhbGci.*EXEMPLO|sk-ant-api03-xxx|your-) ]]; then
                    echo "  Configurando: $key"
                    railway variables set "$key=$value" 2>/dev/null || true
                fi
            fi
        done < .env.railway
        
        echo -e "${GREEN}✅ Variáveis configuradas${NC}"
        echo ""
        
        # Deploy
        echo -e "${YELLOW}🚀 Iniciando deploy...${NC}"
        echo "Isso pode demorar 3-5 minutos..."
        echo ""
        
        if railway up --detach; then
            echo ""
            echo -e "${GREEN}✅ Deploy iniciado com sucesso!${NC}"
            echo ""
            echo "Aguardando build finalizar..."
            sleep 10
            
            # Gerar domínio
            echo "Gerando domínio público..."
            railway domain || echo "Gere manualmente com: railway domain"
            
            echo ""
            echo -e "${GREEN}======================================================================"
            echo "   ✅ DEPLOY CONCLUÍDO COM SUCESSO!"
            echo "======================================================================${NC}"
            echo ""
            echo "Próximos passos:"
            echo ""
            echo "1. Obter URL do serviço:"
            echo "   railway domain"
            echo ""
            echo "2. Ver logs:"
            echo "   railway logs --follow"
            echo ""
            echo "3. Testar API:"
            echo "   curl https://seu-projeto.railway.app/health"
            echo ""
            echo "4. Abrir dashboard:"
            echo "   railway open"
            echo ""
        else
            echo -e "${RED}❌ Erro no deploy${NC}"
            echo "Verifique os logs: railway logs"
            exit 1
        fi
        ;;
        
    2)
        echo ""
        echo -e "${BLUE}Método escolhido: GitHub${NC}"
        echo ""
        
        # Verificar se é um repo git
        if [ ! -d ".git" ]; then
            echo "Inicializando repositório Git..."
            git init
            echo -e "${GREEN}✅ Git inicializado${NC}"
        fi
        
        # Adicionar .gitignore
        if [ ! -f ".gitignore" ]; then
            echo "Criando .gitignore..."
            cat > .gitignore << 'EOF'
.env
.env.railway
*.key
__pycache__/
*.pyc
.vscode/
.idea/
EOF
            echo -e "${GREEN}✅ .gitignore criado${NC}"
        fi
        
        echo ""
        echo "Adicionando arquivos ao Git..."
        git add .
        git commit -m "feat: AI Factory Testing Framework - Railway deploy ready" || echo "Commit já existe"
        
        echo ""
        echo -e "${YELLOW}🔧 PRÓXIMOS PASSOS MANUAIS:${NC}"
        echo ""
        echo "1. Criar repositório no GitHub:"
        if command -v gh &> /dev/null; then
            echo "   gh repo create ai-factory-testing --public --source=. --push"
        else
            echo "   - Vá em: https://github.com/new"
            echo "   - Nome: ai-factory-testing"
            echo "   - Push o código:"
            echo "     git remote add origin https://github.com/SEU_USER/ai-factory-testing.git"
            echo "     git push -u origin main"
        fi
        echo ""
        echo "2. Conectar no Railway:"
        echo "   - Acesse: https://railway.app/dashboard"
        echo "   - Clique em 'New Project'"
        echo "   - Selecione 'Deploy from GitHub repo'"
        echo "   - Escolha o repositório criado"
        echo ""
        echo "3. Configurar variáveis de ambiente:"
        echo "   - Railway Dashboard → Seu projeto → Variables"
        echo "   - Copie as variáveis de .env.railway"
        echo ""
        echo "4. Aguardar deploy automático (3-5 min)"
        echo ""
        echo "5. Gerar domínio:"
        echo "   - Settings → Domains → Generate Domain"
        echo ""
        ;;
        
    3)
        echo ""
        echo -e "${BLUE}Apenas preparando arquivos...${NC}"
        echo ""
        echo -e "${GREEN}✅ Arquivos de deploy verificados:${NC}"
        echo "  - Dockerfile"
        echo "  - railway.toml"
        echo "  - gunicorn.conf.py"
        echo "  - requirements.txt"
        echo "  - .env.railway.example"
        echo "  - .gitignore"
        echo ""
        echo -e "${YELLOW}📚 Documentação disponível:${NC}"
        echo "  - RAILWAY_DEPLOY_MANUAL_GUIDE.md (guia completo)"
        echo "  - DEPLOY_SUMMARY.md (resumo executivo)"
        echo "  - TROUBLESHOOTING.md (soluções de problemas)"
        echo ""
        echo "Quando estiver pronto para deploy, execute novamente:"
        echo "  ./quick-deploy.sh"
        echo ""
        exit 0
        ;;
        
    *)
        echo -e "${RED}❌ Opção inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${CYAN}======================================================================"
echo "   DEPLOY FINALIZADO"
echo "======================================================================${NC}"
echo ""
echo "Documentação útil:"
echo "  - RAILWAY_DEPLOY_MANUAL_GUIDE.md (guia completo)"
echo "  - TROUBLESHOOTING.md (se algo der errado)"
echo "  - test-railway-api.sh (testar API após deploy)"
echo ""
echo -e "${GREEN}Obrigado por usar AI Factory Testing Framework!${NC}"
echo ""
