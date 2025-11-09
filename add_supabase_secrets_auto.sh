#!/bin/bash
set -e

echo "🔐 Adicionando secrets do Supabase no GitHub..."

# Verificar se gh CLI está instalado
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) não está instalado"
    echo "📦 Instale com: brew install gh"
    exit 1
fi

# Verificar autenticação
if ! gh auth status &> /dev/null; then
    echo "🔑 Fazendo login no GitHub..."
    gh auth login
fi

# Adicionar secrets
echo "📝 Adicionando SUPABASE_URL..."
echo "https://pqqrodiuuhckvdqawgeg.supabase.co" | gh secret set SUPABASE_URL

echo "📝 Adicionando SUPABASE_ANON_KEY..."
echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxcXJvZGl1dWhja3ZkcWF3Z2VnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI0OTI0MTIsImV4cCI6MjA3ODA2ODQxMn0.ve7NIbFcZdTGa16O3Pttmpx2mxWgklvbPwwTSCHuDFs" | gh secret set SUPABASE_ANON_KEY

echo ""
echo "✅ Secrets adicionados com sucesso!"
echo ""
echo "📋 Verificando secrets..."
gh secret list

echo ""
echo "🎉 Processo concluído!"
echo ""
echo "📝 Próximos passos:"
echo "1. Fazer push para triggerar novo deploy"
echo "2. Aguardar deploy completar"
echo "3. Verificar logs do Cloud Run"
