# Dashboard Deploy - Vercel

**Production URL**: https://dashboard-5hicey8fn-marcosdanielsfs-projects.vercel.app
**Preview URL**: https://dashboard-it4kfpk55-marcosdanielsfs-projects.vercel.app
**Project Dashboard**: https://vercel.com/marcosdanielsfs-projects/dashboard

## Deployment Status

- Status: DEPLOYED
- Build Time: 32 segundos
- Region: Washington, D.C., USA (East) - iad1
- Build Machine: 2 cores, 8 GB RAM

## Variáveis de Ambiente

Configuradas para todos os ambientes (production, preview, development):

- `NEXT_PUBLIC_API_URL`: https://ai-factory-api.railway.app
- `NEXT_PUBLIC_SUPABASE_URL`: https://bfumywvwubvernvhjehk.supabase.co
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: [Configurado via Vercel Dashboard]

## Comandos Úteis

```bash
# Deploy para produção
vercel --prod

# Ver logs do último deploy
vercel logs

# Rollback para deploy anterior
vercel rollback

# Inspecionar deploy específico
vercel inspect <deployment-url> --logs

# Adicionar variável de ambiente
vercel env add <VAR_NAME> <environment>

# Listar variáveis de ambiente
vercel env ls

# Pull das variáveis para .env.local
vercel env pull
```

## Métricas de Build

- **Build Time**: 32 segundos
- **Compilation**: 9.2s (Turbopack)
- **TypeScript Check**: ~4.5s
- **Static Generation**: 286ms
- **Serverless Functions**: 133ms
- **Static Files Collection**: 4.9ms

## Rotas Deployadas

- `/` - Dashboard Home (Static)
- `/agents` - Lista de Agentes (Static)
- `/agents/[id]` - Detalhe do Agente (Dynamic)
- `/tests` - Testes (Static)
- `/_not-found` - 404 Page (Static)

## Pacotes Instalados

- Total: 457 pacotes
- Vulnerabilidades: 0
- Tempo de instalação: 15s

## Próximos Passos

1. Aguardar Railway URL do Agent #6 (já configurado)
2. Testar conexão frontend com backend
3. Validar autenticação Supabase
4. Executar testes E2E
5. Validar performance com Lighthouse

## Troubleshooting

### Build Errors
Se houver erros de build, execute localmente:
```bash
npm run build
```

### Variáveis de Ambiente
Para atualizar variáveis de ambiente:
```bash
vercel env rm <VAR_NAME> production
vercel env add <VAR_NAME> production
```

### Cache Issues
Para forçar rebuild sem cache:
```bash
vercel --prod --force
```

## Observações

- Next.js 16.1.1 usando Turbopack
- Build otimizado para produção
- Static pages pré-renderizadas
- TypeScript compilado com sucesso
- Sem vulnerabilidades detectadas
